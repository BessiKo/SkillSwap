from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, BadgeType

class BadgeOut(BaseModel):
    name: str
    type: BadgeType
    icon: str
    description: str
    
    class Config:
        from_attributes = True

class UserProfileOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    bio: str
    university: str
    faculty: str
    year: Optional[int] = None
    rating: float
    total_ratings: int
    exchanges_completed: int
    reviews_received: int
    badges: list[BadgeOut] = []

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    university: Optional[str] = None
    faculty: Optional[str] = None
    year: Optional[int] = None
    
    class Config:
        extra = "forbid"