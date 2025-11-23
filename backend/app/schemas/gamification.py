# app/schemas/gamification.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class BadgeType(str, Enum):
    """Типы значков для геймификации."""
    NEWCOMER = "newcomer"
    FIRST_EXCHANGE = "first_exchange"
    POPULAR = "popular"
    TOP_RATED = "top_rated"
    MENTOR = "mentor"
    EXPERT = "expert"
    CATEGORY_EXPERT = "category_expert"

class BadgeCreate(BaseModel):
    """Схема для создания значка."""
    name: str = Field(..., max_length=50, description="Название значка")
    type: BadgeType = Field(..., description="Тип значка")
    description: str = Field(..., max_length=255, description="Описание значка")
    icon: str = Field(..., max_length=10, description="Иконка значка (эмодзи)")

    @validator('name')
    def name_length(cls, v):
        if len(v) > 50:
            raise ValueError('Name must be 50 characters or less')
        return v

    @validator('description')
    def description_length(cls, v):
        if len(v) > 255:
            raise ValueError('Description must be 255 characters or less')
        return v

    @validator('icon')
    def icon_length(cls, v):
        if len(v) > 10:
            raise ValueError('Icon must be 10 characters or less')
        return v

    class Config:
        from_attributes = True

class BadgeOut(BaseModel):
    """Схема значка для вывода."""
    id: int
    name: str
    type: BadgeType
    description: str
    icon: str
    
    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    """Схема для создания отзыва."""
    target_user_id: str = Field(..., description="ID пользователя, которому оставляем отзыв")
    deal_id: int = Field(..., description="ID сделки, по которой оставляем отзыв")
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    text: Optional[str] = Field(None, max_length=1000, description="Текст отзыва")

    @validator('text')
    def text_length(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Text must be 1000 characters or less')
        return v

    class Config:
        from_attributes = True

class ReviewOut(BaseModel):
    """Схема отзыва для вывода."""
    id: int
    author_id: str
    target_user_id: str
    deal_id: int
    rating: int
    text: Optional[str]
    created_at: datetime
    author_name: str
    author_avatar: Optional[str]
    
    class Config:
        from_attributes = True

class UserStatsOut(BaseModel):
    """Статистика пользователя."""
    reputation: int = Field(..., description="Общая репутация")
    exchanges_completed: int = Field(..., description="Количество завершенных обменов")
    total_ratings: int = Field(..., description="Общее количество оценок")
    average_rating: float = Field(..., ge=0, le=5, description="Средний рейтинг")
    level: int = Field(..., ge=1, description="Текущий уровень")
    experience: int = Field(..., ge=0, description="Текущий опыт")
    next_level_exp: int = Field(..., ge=1, description="Опыт до следующего уровня")

    programming_exchanges: int = Field(0, description="Обмены в программировании")
    design_exchanges: int = Field(0, description="Обмены в дизайне")
    languages_exchanges: int = Field(0, description="Обмены в языках")
    math_exchanges: int = Field(0, description="Обмены в математике")
    science_exchanges: int = Field(0, description="Обмены в науках")
    business_exchanges: int = Field(0, description="Обмены в бизнесе")
    music_exchanges: int = Field(0, description="Обмены в музыке")
    sports_exchanges: int = Field(0, description="Обмены в спорте")
    other_exchanges: int = Field(0, description="Обмены в других категориях")

    @validator('average_rating')
    def validate_rating(cls, v):
        return round(v, 2)

    class Config:
        from_attributes = True

class UserProfileGamifiedOut(BaseModel):
    """Расширенная схема профиля с геймификацией."""

    id: str = Field(..., description="ID пользователя")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
    university: str = Field(..., description="Университет")
    faculty: str = Field(..., description="Факультет")
    year: Optional[int] = Field(None, description="Год обучения")
    bio: str = Field(..., description="Биография")
    stats: UserStatsOut = Field(..., description="Статистика")
    badges: List[BadgeOut] = Field(..., description="Значки")
    reviews: List[ReviewOut] = Field(..., description="Отзывы")
    
    class Config:
        from_attributes = True

class LevelProgressOut(BaseModel):
    """Прогресс уровня."""
    current_level: int = Field(..., ge=1, description="Текущий уровень")
    current_exp: int = Field(..., ge=0, description="Текущий опыт")
    next_level_exp: int = Field(..., ge=1, description="Опыт до следующего уровня")
    progress_percentage: float = Field(..., ge=0, le=100, description="Процент прогресса")

    @validator('progress_percentage')
    def validate_percentage(cls, v):
        return round(v, 2)

    class Config:
        from_attributes = True

class LeaderboardUserOut(BaseModel):
    """Пользователь для таблицы лидеров."""
    id: str = Field(..., description="ID пользователя")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
    university: str = Field(..., description="Университет")
    reputation: int = Field(..., description="Репутация")
    level: int = Field(..., description="Уровень")
    position: int = Field(..., ge=1, description="Позиция в рейтинге")

    class Config:
        from_attributes = True

class GlobalStatsOut(BaseModel):
    """Глобальная статистика платформы."""
    total_users: int = Field(..., description="Всего пользователей")
    total_exchanges: int = Field(..., description="Всего обменов")
    total_reviews: int = Field(..., description="Всего отзывов")
    average_rating: float = Field(..., description="Средний рейтинг")
    most_popular_category: str = Field(..., description="Самая популярная категория")
    top_university: str = Field(..., description="Топовый университет")
    active_this_week: int = Field(..., description="Активных за неделю")
    new_users_today: int = Field(..., description="Новых пользователей сегодня")

    @validator('average_rating')
    def validate_rating(cls, v):
        return round(v, 2)

    class Config:
        from_attributes = True

class AchievementOut(BaseModel):
    """Схема достижения."""
    id: int = Field(..., description="ID достижения")
    name: str = Field(..., description="Название достижения")
    description: str = Field(..., description="Описание достижения")
    unlocked_at: Optional[datetime] = Field(None, description="Когда разблокировано")
    icon: str = Field(..., description="Иконка достижения")

    class Config:
        from_attributes = True

class NextAchievementOut(BaseModel):
    """Схема следующего достижения."""
    id: int = Field(..., description="ID достижения")
    name: str = Field(..., description="Название достижения")
    description: str = Field(..., description="Описание достижения")
    progress: int = Field(..., description="Текущий прогресс")
    required: int = Field(..., description="Требуемое значение")
    progress_percentage: float = Field(..., description="Процент прогресса")

    @validator('progress_percentage')
    def validate_percentage(cls, v):
        return round(v, 2)

    class Config:
        from_attributes = True

class UserAchievementsOut(BaseModel):
    """Достижения пользователя."""
    user_id: str = Field(..., description="ID пользователя")
    unlocked_achievements: List[AchievementOut] = Field(..., description="Разблокированные достижения")
    next_achievements: List[NextAchievementOut] = Field(..., description="Следующие достижения")

    class Config:
        from_attributes = True

class BadgeAwardResponse(BaseModel):
    """Ответ на выдачу значка."""
    message: str = Field(..., description="Сообщение")
    user_id: str = Field(..., description="ID пользователя")
    badge_id: int = Field(..., description="ID значка")
    badge_name: str = Field(..., description="Название значка")

    class Config:
        from_attributes = True

class DetailedStatsOut(BaseModel):
    """Детальная статистика геймификации."""
    total_badges: int = Field(..., description="Всего значков")
    users_with_badges: int = Field(..., description="Пользователей со значками")
    badge_distribution_rate: float = Field(..., description="Процент распределения значков")
    most_awarded_badges: List[dict] = Field(..., description="Самые выдаваемые значки")

    @validator('badge_distribution_rate')
    def validate_rate(cls, v):
        return round(v, 2)

    class Config:
        from_attributes = True