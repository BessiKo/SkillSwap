from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import enum
from uuid import uuid4
from typing import List, TYPE_CHECKING, Optional
from datetime import datetime

if TYPE_CHECKING:
    from app.models.ad import Ad

class UserRole(str, enum.Enum):
    """Роли пользователей в системе."""
    STUDENT = "student"
    ADMIN = "admin"

class BadgeType(str, enum.Enum):
    """Типы значков (для упрощенного сидинга)."""
    NEWCOMER = "newcomer"
    FIRST_EXCHANGE = "first_exchange"
    POPULAR = "popular"
    TOP_RATED = "top_rated"
    MENTOR = "mentor"
    EXPERT = "expert"

user_badges = Table(
    "user_badges", Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("badge_id", Integer, ForeignKey("badges.id"), primary_key=True),
    Column("awarded_at", DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    """Основная модель пользователя."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True) 
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    profile: Mapped["UserProfile"] = relationship("UserProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    badges: Mapped[List["Badge"]] = relationship("Badge", secondary=user_badges, back_populates="users")
    ads: Mapped[List["Ad"]] = relationship("Ad", back_populates="author", cascade="all, delete-orphan")
    admin_actions = relationship("AdminLog", foreign_keys="AdminLog.admin_id", back_populates="admin")

    def __repr__(self):
        return f"<User id={self.id}, phone={self.phone}, role={self.role.value}>"

class UserProfile(Base):
    """Детали профиля пользователя (имя, вуз, рейтинг и т.д.)."""
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)

    first_name: Mapped[str] = mapped_column(String(100), default="")
    last_name: Mapped[str] = mapped_column(String(100), default="")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, default="")

    university: Mapped[str] = mapped_column(String(200), default="")
    faculty: Mapped[str] = mapped_column(String(200), default="")
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    rating: Mapped[float] = mapped_column(Float, default=0.0)
    total_ratings: Mapped[int] = mapped_column(Integer, default=0)
    exchanges_completed: Mapped[int] = mapped_column(Integer, default=0)
    reviews_received: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id}, name={self.first_name} {self.last_name}>"

class Badge(Base):
    """Модель значков, которые можно присваивать пользователям."""
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[BadgeType] = mapped_column(Enum(BadgeType), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), nullable=False)

    users: Mapped[List["User"]] = relationship("User", secondary=user_badges, back_populates="badges")

    def __repr__(self):
        return f"<Badge {self.name} ({self.type.value})>"