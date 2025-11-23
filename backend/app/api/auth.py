from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from app.schemas.auth import (
    PhoneRequest, CodeVerifyRequest, TokenResponse, CodeRequestResponse
)
from app.services.auth import AuthService, get_auth_service, create_tokens 
from app.api.deps import get_refresh_token
from app.utils.security import decode_token, verify_token_type
from app.config import settings
from app.models.user import User 

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/request_code", response_model=CodeRequestResponse)
async def request_verification_code(
    data: PhoneRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request SMS verification code.
    Rate limited to 5 requests per hour per phone number.
    """
    success, message, debug_code = await auth_service.request_code(data.phone)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS if "Too many" in message else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return CodeRequestResponse(
        message=message,
        expires_in=settings.CODE_EXPIRY,
        debug_code=debug_code
    )

@router.post("/verify_code", response_model=TokenResponse)
async def verify_code(
    data: CodeVerifyRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify SMS code. If correct, return Access Token and set Refresh Token in HTTP-only cookie.
    """
    user, is_new_user, error = await auth_service.verify_code(data.phone, data.code)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    access_token, access_exp, refresh_token, refresh_exp = create_tokens(user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,

        samesite="lax",
        max_age=refresh_exp,
        path="/api/v1/auth" 
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=access_exp,
        is_new_user=is_new_user
    )


@router.post("/refresh_token", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    refresh_token: str = Depends(get_refresh_token), 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh Access Token using Refresh Token from cookie (token rotation).
    """
    token_payload = decode_token(refresh_token)
    
    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh-token"
        )
    
    if not verify_token_type(token_payload, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
 
    user: User | None = await auth_service.get_user_by_id(token_payload.sub) 
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    if not user.is_active: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь неактивен"
        )

    access_token, access_exp, new_refresh_token, refresh_exp = create_tokens(user)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,

        samesite="lax",
        max_age=refresh_exp,
        path="/api/v1/auth"
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=access_exp,
        is_new_user=False
    )

@router.post("/logout")
async def logout(response: Response):
    """
    Deletes the Refresh Token cookie.
    """

    response.delete_cookie(
        key="refresh_token",
        httponly=True,

        samesite="lax",
        path="/api/v1/auth"
    )
    return {"message": "Logout successful"}