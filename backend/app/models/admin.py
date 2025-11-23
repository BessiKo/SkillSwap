from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import enum
from typing import TYPE_CHECKING, Optional
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.ad import Ad
    from app.models.chat import Chat
    from app.models.deal import Deal

class AdminActionType(str, enum.Enum):
    """Типы действий администратора."""
    USER_BANNED = "user_banned"
    USER_UNBANNED = "user_unbanned"
    AD_DELETED = "ad_deleted"
    AD_HIDDEN = "ad_hidden"
    AD_RESTORED = "ad_restored"
    CHAT_DELETED = "chat_deleted"
    DEAL_CANCELLED = "deal_cancelled"
    DEAL_MODIFIED = "deal_modified"

class AdminLog(Base):
    """Лог действий администратора."""
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action_type = Column(Enum(AdminActionType), nullable=False)

    target_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    target_ad_id = Column(String(36), ForeignKey("ads.id"), nullable=True)
    target_chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)
    target_deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)

    reason = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    admin = relationship("User", foreign_keys=[admin_id], back_populates="admin_actions")
    target_user = relationship("User", foreign_keys=[target_user_id])
    target_ad = relationship("Ad")
    target_chat = relationship("Chat")
    target_deal = relationship("Deal")

    def __repr__(self):
        return f"<AdminLog {self.action_type.value} by {self.admin_id}>"