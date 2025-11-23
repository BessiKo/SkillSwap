from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

from app.models.ad import AdCategory, AdLevel, AdFormat

class AdCreate(BaseModel):
    """Схема для создания объявления."""
    category: AdCategory
    title: str = Field(..., max_length=120)
    description: str
    level: AdLevel
    format: AdFormat

    @validator('title')
    def title_length(cls, v):
        if len(v) > 120:
            raise ValueError('Title must be 120 characters or less')
        return v

class AdUpdate(BaseModel):
    """Схема для обновления объявления."""
    category: Optional[AdCategory] = None
    title: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None
    level: Optional[AdLevel] = None
    format: Optional[AdFormat] = None

    @validator('title')
    def title_length(cls, v):
        if v is not None and len(v) > 120:
            raise ValueError('Title must be 120 characters or less')
        return v

class AuthorOut(BaseModel):
    """Упрощенная схема автора для вывода в объявлениях."""
    id: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    rating: float

    class Config:
        from_attributes = True

class AdOut(BaseModel):
    """Полная схема объявления для вывода."""
    id: str
    author: AuthorOut
    category: AdCategory
    title: str
    description: str
    level: AdLevel
    format: AdFormat
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdListOut(BaseModel):
    """Схема для списка объявлений с пагинацией."""
    items: list[AdOut]
    total: int
    page: int
    pages: int

class AdFilter(BaseModel):
    """Параметры фильтрации для ленты объявлений."""
    category: Optional[AdCategory] = None
    level: Optional[AdLevel] = None
    format: Optional[AdFormat] = None
    q: Optional[str] = None
    sort: str = "newest"
    page: int = 1
    page_size: int = 20