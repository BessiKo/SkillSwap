from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.admin import AdminActionType
from app.models.deal import DealStatus
from app.schemas.user import UserProfileOut
from app.schemas.ad import AdOut

class AdminActionType(str, Enum):
    USER_BANNED = "user_banned"
    USER_UNBANNED = "user_unbanned"
    AD_DELETED = "ad_deleted"
    AD_HIDDEN = "ad_hidden"
    AD_RESTORED = "ad_restored"
    CHAT_DELETED = "chat_deleted"
    DEAL_CANCELLED = "deal_cancelled"
    DEAL_MODIFIED = "deal_modified"

class UserBanRequest(BaseModel):
    """Схема для блокировки пользователя."""
    reason: Optional[str] = None
    details: Optional[str] = None

class AdminActionRequest(BaseModel):
    """Базовая схема для действий администратора."""
    reason: Optional[str] = None
    details: Optional[str] = None

class AdminLogOut(BaseModel):
    """Схема для вывода логов администратора."""
    id: int
    admin_id: str
    action_type: AdminActionType
    target_user_id: Optional[str] = None
    target_ad_id: Optional[str] = None
    target_chat_id: Optional[int] = None
    target_deal_id: Optional[int] = None
    reason: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

    admin: Optional[UserProfileOut] = None
    target_user: Optional[UserProfileOut] = None
    target_ad: Optional[AdOut] = None

    class Config:
        from_attributes = True

class MessageAdminOut(BaseModel):
    """Схема для сообщений в админ-панели."""
    id: int
    chat_id: int
    sender: UserProfileOut
    text: str
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatAdminOut(BaseModel):
    """Схема для чатов в админ-панели."""
    id: int
    ad: AdOut
    user1: UserProfileOut
    user2: UserProfileOut
    created_at: datetime
    messages: List[MessageAdminOut] = []
    has_deal: bool = False

    class Config:
        from_attributes = True

class DealAdminOut(BaseModel):
    """Схема для сделок в админ-панели."""
    id: int
    chat_id: int
    status: DealStatus
    student: UserProfileOut
    teacher: UserProfileOut
    proposed_skill: Optional[str] = None
    proposed_time: Optional[str] = None
    proposed_place: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdminStatsOut(BaseModel):
    """Статистика для админ-панели."""
    total_users: int
    total_ads: int
    total_chats: int
    total_deals: int
    active_users: int
    active_ads: int
    banned_users: int
    recent_actions: List[AdminLogOut] = []

    class Config:
        from_attributes = True

class UserListOut(BaseModel):
    """Схема для списка пользователей в админ-панели."""
    id: str
    phone: str
    role: str
    is_active: bool
    created_at: datetime
    profile: Optional[UserProfileOut] = None
    ads_count: int = 0
    chats_count: int = 0
    deals_count: int = 0

    class Config:
        from_attributes = True

class AdListAdminOut(BaseModel):
    """Схема для списка объявлений в админ-панели."""
    id: str
    title: str
    category: str
    level: str
    format: str
    created_at: datetime
    author: UserProfileOut
    is_active: bool = True
    chats_count: int = 0

    class Config:
        from_attributes = True