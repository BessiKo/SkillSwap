from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis 
import logging
from typing import Tuple, Optional

from app.config import settings
from app.services.sms import SMSProvider, get_sms_provider 
from app.models.user import User, UserRole
from app.utils.security import generate_verification_code, create_access_token, create_refresh_token
from app.database import get_db, get_redis 

logger = logging.getLogger(__name__)

def create_tokens(user: User) -> Tuple[str, int, str, int]:
    """
    Creates Access and Refresh tokens for a User object.
    Returns: (access_token, access_exp, refresh_token, refresh_exp)
    """
    user_id = str(user.id) 
    role = str(user.role.value) 
    
    access_token, access_exp = create_access_token(user_id, role)
    refresh_token, refresh_exp = create_refresh_token(user_id, role)
    
    return access_token, access_exp, refresh_token, refresh_exp

async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    """Retrieves a user by phone number."""
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    return result.scalars().first()

async def create_new_user(db: AsyncSession, phone: str) -> User:
    """Creates a new user with the STUDENT role."""
    new_user = User(phone=phone, role=UserRole.STUDENT) 
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_id_dao(db: AsyncSession, user_id: str) -> Optional[User]:
    """Retrieves a user by ID (UUID)."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalars().first()


class AuthService:
    """Service for phone authentication, rate limiting, and code management."""
    def __init__(self, db: AsyncSession, redis: Redis, sms_provider: SMSProvider):
        self.db = db
        self.redis = redis
        self.sms_provider = sms_provider

        self.limit = settings.CODE_REQUEST_LIMIT
        self.window = settings.CODE_REQUEST_WINDOW

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Method used by router/dependency to get a user by token ID (UUID)."""
        return await get_user_by_id_dao(self.db, user_id)

    async def request_code(self, phone: str) -> Tuple[bool, str, Optional[str]]:
        """
        Generates and sends an SMS code, handling request limits.
        Returns: (success, message, debug_code)
        """
        rate_key = f"auth:ratelimit:{phone}"
        
        count = await self.redis.incr(rate_key)
        
        if count == 1:
 
            await self.redis.expire(rate_key, self.window)

        if count > self.limit:
          
            await self.redis.decr(rate_key) 
            minutes = self.window // 60
            return False, f"Too many requests. Limit is {self.limit} per {minutes} minutes.", None

        code = generate_verification_code()
        code_expiry = settings.CODE_EXPIRY
        code_key = f"auth:code:{phone}"
        
        await self.redis.set(code_key, code, ex=code_expiry)

        success = await self.sms_provider.send_code(phone, code)
        
        if not success:
            logger.error(f"Failed to send SMS to {phone} for code {code}")

            await self.redis.decr(rate_key)
            return False, "Failed to send SMS. Please try again.", None
            
        logger.info(f"Verification code requested and stored for {phone}")

        debug_code = code if settings.DEBUG else None 

        return True, "Verification code sent successfully.", debug_code

    async def verify_code(self, phone: str, submitted_code: str) -> Tuple[Optional[User], bool, Optional[str]]:
        """
        Verifies the code, and if successful, finds or creates a user.
        Returns: (user, is_new, error)
        """
        code_key = f"auth:code:{phone}"
        stored_code = await self.redis.get(code_key)
        
        if not stored_code:
            return None, False, "Verification code expired or not requested."

        if stored_code != submitted_code:
            return None, False, "Invalid verification code."

        await self.redis.delete(code_key)

        user = await get_user_by_phone(self.db, phone)
        is_new = False
        
        if user is None:
            user = await create_new_user(self.db, phone)
            is_new = True

        return user, is_new, None

def get_auth_service(
    db: AsyncSession = Depends(get_db), 
    redis: Redis = Depends(get_redis), 
    sms_provider: SMSProvider = Depends(get_sms_provider), 
) -> AuthService:
    """DI for the Authentication Service."""
    return AuthService(db=db, redis=redis, sms_provider=sms_provider)