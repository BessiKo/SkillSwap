from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import settings
from app.schemas.auth import TokenPayload
import secrets


def create_access_token(user_id: str, role: str) -> tuple[str, int]:
    """Create JWT access token. Returns (token, expires_in_seconds)."""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire.timestamp(), 
        "type": "access"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, int(expires_delta.total_seconds())

def create_refresh_token(user_id: str, role: str) -> tuple[str, int]:
    """Create JWT refresh token. Returns (token, expires_in_seconds)."""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire.timestamp(),
        "type": "refresh"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, int(expires_delta.total_seconds())

def decode_token(token: str) -> TokenPayload | None:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)
    except JWTError:
        return None

def verify_token_type(payload: TokenPayload, expected_type: str) -> bool:
    """Check if the token type matches the expected type."""
    return payload.type == expected_type

def generate_verification_code() -> str:
    """Generate 6-digit verification code."""
    return "".join([str(secrets.randbelow(10)) for _ in range(6)])