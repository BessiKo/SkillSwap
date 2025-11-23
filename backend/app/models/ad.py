from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import enum
from uuid import uuid4
from typing import TYPE_CHECKING, Optional
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User

class AdCategory(str, enum.Enum):
    """Категории объявлений."""
    PROGRAMMING = "programming"
    DESIGN = "design"
    LANGUAGES = "languages"
    MATH = "math"
    SCIENCE = "science"
    BUSINESS = "business"
    MUSIC = "music"
    SPORTS = "sports"
    OTHER = "other"

class AdLevel(str, enum.Enum):
    """Уровень сложности."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class AdFormat(str, enum.Enum):
    """Формат проведения."""
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"

class Ad(Base):
    """Модель объявления."""
    __tablename__ = "ads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    category: Mapped[AdCategory] = mapped_column(Enum(AdCategory), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[AdLevel] = mapped_column(Enum(AdLevel), nullable=False, index=True)
    format: Mapped[AdFormat] = mapped_column(Enum(AdFormat), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    author: Mapped["User"] = relationship("User", back_populates="ads")
    chats = relationship("Chat", back_populates="ad", cascade="all, delete-orphan")  # Добавлено

    def __repr__(self):
        return f"<Ad id={self.id}, title='{self.title}', author_id={self.author_id}>"

Index('idx_ads_category_level', Ad.category, Ad.level)
Index('idx_ads_author_created', Ad.author_id, Ad.created_at.desc())
Index('idx_ads_created', Ad.created_at.desc())