from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserProfileOut, UserUpdate
from app.api.deps import get_current_active_user

router = APIRouter(tags=["Users"])

@router.get("/me", response_model=UserProfileOut)
async def read_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение профиля текущего аутентифицированного пользователя.
    """
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return UserProfileOut.model_validate(current_user.profile)

@router.patch("/me", response_model=UserProfileOut)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление профиля текущего аутентифицированного пользователя.
    """
    profile = current_user.profile
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    
    return UserProfileOut.model_validate(profile)