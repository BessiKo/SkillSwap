# app/models/gamification.py
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import enum
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User

class BadgeType(str, enum.Enum):
    """Типы значков для геймификации."""
    NEWCOMER = "newcomer"
    FIRST_EXCHANGE = "first_exchange"
    POPULAR = "popular"
    TOP_RATED = "top_rated"
    MENTOR = "mentor"
    EXPERT = "expert"
    CATEGORY_EXPERT = "category_expert"

class Badge(Base):
    """Модель значка для геймификации."""
    __tablename__ = "gamification_badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[BadgeType] = mapped_column(Enum(BadgeType), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), nullable=False)

    def __repr__(self):
        return f"<Badge {self.name} ({self.type.value})>"