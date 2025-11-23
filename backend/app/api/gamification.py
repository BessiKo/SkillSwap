from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.api.deps import get_current_active_user, get_admin_user
from app.models.user import User
from app.schemas.gamification import (
    ReviewCreate, ReviewOut, UserProfileGamifiedOut, 
    LevelProgressOut, LeaderboardUserOut, BadgeOut,
    BadgeCreate, GlobalStatsOut, UserAchievementsOut,
    BadgeAwardResponse, DetailedStatsOut
)

router = APIRouter(prefix="/gamification", tags=["Gamification"])

@router.get("/test")
async def gamification_test():
    """Тестовый endpoint для геймификации."""
    return {
        "message": "🎮 Gamification system is working!",
        "status": "active",
        "version": "1.0.0",
        "features": [
            "badges", 
            "reviews", 
            "leaderboard", 
            "levels",
            "reputation",
            "experience_system"
        ]
    }

@router.post("/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создание отзыва о пользователе.
    
    - **target_user_id**: ID пользователя, которому оставляем отзыв
    - **deal_id**: ID сделки, по которой оставляем отзыв  
    - **rating**: Оценка от 1 до 5
    - **text**: Текст отзыва (опционально)
    """

    return {
        "id": 1,
        "author_id": str(current_user.id),
        "target_user_id": review_data.target_user_id,
        "deal_id": review_data.deal_id,
        "rating": review_data.rating,
        "text": review_data.text,
        "created_at": "2024-01-01T00:00:00Z",
        "author_name": f"{current_user.profile.first_name} {current_user.profile.last_name}",
        "author_avatar": current_user.profile.avatar_url
    }

@router.get("/profile/{user_id}", response_model=UserProfileGamifiedOut)
async def get_user_profile_gamified(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение профиля пользователя с геймификацией.
    
    Включает:
    - Основную информацию пользователя
    - Статистику и уровни
    - Значки и достижения
    - Отзывы
    """

    return {
        "id": user_id,
        "first_name": "Иван",
        "last_name": "Иванов",
        "avatar_url": "https://example.com/avatar.jpg",
        "university": "МГУ",
        "faculty": "Факультет компьютерных наук",
        "year": 2024,
        "bio": "Люблю учиться и делиться знаниями!",
        "stats": {
            "reputation": 150,
            "exchanges_completed": 15,
            "total_ratings": 12,
            "average_rating": 4.8,
            "level": 3,
            "experience": 75,
            "next_level_exp": 100,
            "programming_exchanges": 8,
            "design_exchanges": 2,
            "languages_exchanges": 3,
            "math_exchanges": 1,
            "science_exchanges": 1,
            "business_exchanges": 0,
            "music_exchanges": 0,
            "sports_exchanges": 0,
            "other_exchanges": 0
        },
        "badges": [
            {
                "id": 1,
                "name": "Новичок",
                "type": "newcomer",
                "description": "Добро пожаловать в Скилл Свап!",
                "icon": "👋"
            },
            {
                "id": 2,
                "name": "Первый обмен", 
                "type": "first_exchange",
                "description": "Провёл первый обмен знаниями",
                "icon": "🎯"
            },
            {
                "id": 3,
                "name": "Популярный",
                "type": "popular", 
                "description": "10+ успешных обменов",
                "icon": "⭐"
            }
        ],
        "reviews": [
            {
                "id": 1,
                "author_id": "user456",
                "target_user_id": user_id,
                "deal_id": 1,
                "rating": 5,
                "text": "Отличный преподаватель! Очень понятно объясняет сложные темы.",
                "created_at": "2024-01-15T10:30:00Z",
                "author_name": "Мария Петрова",
                "author_avatar": "https://example.com/avatar2.jpg"
            },
            {
                "id": 2,
                "author_id": "user789", 
                "target_user_id": user_id,
                "deal_id": 2,
                "rating": 4,
                "text": "Хороший обмен, рекомендую!",
                "created_at": "2024-01-20T14:45:00Z",
                "author_name": "Алексей Сидоров",
                "author_avatar": "https://example.com/avatar3.jpg"
            }
        ]
    }

@router.get("/my/profile", response_model=UserProfileGamifiedOut)
async def get_my_profile_gamified(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение собственного профиля с геймификацией.
    """

    return await get_user_profile_gamified(str(current_user.id), db)

@router.get("/leaderboard", response_model=List[LeaderboardUserOut])
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100, description="Количество пользователей в таблице лидеров"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение таблицы лидеров.
    
    Сортировка по репутации в порядке убывания.
    """

    leaderboard_data = [
        {
            "id": "user1",
            "first_name": "Анна",
            "last_name": "Смирнова", 
            "avatar_url": "https://example.com/avatar1.jpg",
            "university": "МГУ",
            "reputation": 450,
            "level": 8,
            "position": 1
        },
        {
            "id": "user2",
            "first_name": "Дмитрий",
            "last_name": "Козлов",
            "avatar_url": "https://example.com/avatar2.jpg", 
            "university": "СПбГУ",
            "reputation": 380,
            "level": 7,
            "position": 2
        },
        {
            "id": "user3", 
            "first_name": "Екатерина",
            "last_name": "Новикова",
            "avatar_url": "https://example.com/avatar3.jpg",
            "university": "МФТИ", 
            "reputation": 320,
            "level": 6,
            "position": 3
        },
        {
            "id": "current_user",
            "first_name": "Иван",
            "last_name": "Иванов", 
            "avatar_url": "https://example.com/avatar4.jpg",
            "university": "МГУ",
            "reputation": 150, 
            "level": 3,
            "position": 25
        }
    ]
    
    return leaderboard_data[:limit]

@router.get("/level-progress", response_model=LevelProgressOut)
async def get_level_progress(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение прогресса уровня текущего пользователя.
    
    Показывает:
    - Текущий уровень
    - Накопленный опыт
    - Опыт до следующего уровня
    - Процент прогресса
    """

    current_level = 3
    current_exp = 75
    next_level_exp = 100
    progress_percentage = (current_exp / next_level_exp) * 100
    
    return {
        "current_level": current_level,
        "current_exp": current_exp,
        "next_level_exp": next_level_exp,
        "progress_percentage": round(progress_percentage, 2)
    }

@router.get("/users/{user_id}/reviews", response_model=List[ReviewOut])
async def get_user_reviews(
    user_id: str,
    limit: int = Query(20, ge=1, le=50, description="Количество отзывов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение отзывов о пользователе.
    
    Возвращает список отзывов с пагинацией.
    """

    reviews = [
        {
            "id": 1,
            "author_id": "author1",
            "target_user_id": user_id,
            "deal_id": 1,
            "rating": 5,
            "text": "Отличный преподаватель! Очень понятно объясняет сложные темы.",
            "created_at": "2024-01-15T10:30:00Z",
            "author_name": "Мария Петрова",
            "author_avatar": "https://example.com/avatar2.jpg"
        },
        {
            "id": 2,
            "author_id": "author2",
            "target_user_id": user_id,
            "deal_id": 2,
            "rating": 4,
            "text": "Хороший обмен, рекомендую!",
            "created_at": "2024-01-20T14:45:00Z", 
            "author_name": "Алексей Сидоров",
            "author_avatar": "https://example.com/avatar3.jpg"
        },
        {
            "id": 3,
            "author_id": "author3",
            "target_user_id": user_id,
            "deal_id": 3,
            "rating": 5, 
            "text": "Очень доволен обменом. Профессиональный подход!",
            "created_at": "2024-01-25T16:20:00Z",
            "author_name": "Ольга Кузнецова",
            "author_avatar": "https://example.com/avatar4.jpg"
        }
    ]

    start_index = offset
    end_index = offset + limit
    return reviews[start_index:end_index]

@router.get("/badges", response_model=List[BadgeOut])
async def get_all_badges(
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех доступных значков в системе.
    """

    badges = [
        {
            "id": 1,
            "name": "Новичок",
            "type": "newcomer",
            "description": "Добро пожаловать в Скилл Свап!",
            "icon": "👋"
        },
        {
            "id": 2,
            "name": "Первый обмен",
            "type": "first_exchange", 
            "description": "Провёл первый обмен знаниями",
            "icon": "🎯"
        },
        {
            "id": 3,
            "name": "Популярный",
            "type": "popular",
            "description": "10+ успешных обменов", 
            "icon": "⭐"
        },
        {
            "id": 4,
            "name": "Топ рейтинг",
            "type": "top_rated",
            "description": "Рейтинг 4.8+ с 5+ отзывами",
            "icon": "🏆" 
        },
        {
            "id": 5,
            "name": "Ментор",
            "type": "mentor",
            "description": "25+ успешных обменов",
            "icon": "🎓"
        },
        {
            "id": 6, 
            "name": "Эксперт",
            "type": "expert",
            "description": "50+ успешных обменов",
            "icon": "💎"
        },
        {
            "id": 7,
            "name": "Эксперт по программированию",
            "type": "category_expert", 
            "description": "10+ обменов в программировании",
            "icon": "💻"
        },
        {
            "id": 8,
            "name": "Эксперт по дизайну",
            "type": "category_expert",
            "description": "10+ обменов в дизайне",
            "icon": "🎨"
        },
        {
            "id": 9,
            "name": "Эксперт по языкам",
            "type": "category_expert",
            "description": "10+ обменов в языках", 
            "icon": "🌍"
        }
    ]
    
    return badges

@router.get("/stats/global", response_model=GlobalStatsOut)
async def get_global_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Получение глобальной статистики платформы.
    """
    return {
        "total_users": 1250,
        "total_exchanges": 5432,
        "total_reviews": 4890,
        "average_rating": 4.7,
        "most_popular_category": "programming",
        "top_university": "МГУ",
        "active_this_week": 347,
        "new_users_today": 23
    }

@router.get("/achievements/unlocked", response_model=UserAchievementsOut)
async def get_unlocked_achievements(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение разблокированных достижений текущего пользователя.
    """
    return {
        "user_id": str(current_user.id),
        "unlocked_achievements": [
            {
                "id": 1,
                "name": "Первый шаг",
                "description": "Создал первый профиль",
                "unlocked_at": "2024-01-01T00:00:00Z",
                "icon": "🚶"
            },
            {
                "id": 2,
                "name": "Социальная бабочка",
                "description": "Отправил 10 сообщений в чатах", 
                "unlocked_at": "2024-01-05T12:30:00Z",
                "icon": "🦋"
            },
            {
                "id": 3,
                "name": "Исследователь",
                "description": "Просмотрел 50 объявлений",
                "unlocked_at": "2024-01-10T15:45:00Z",
                "icon": "🔍"
            }
        ],
        "next_achievements": [
            {
                "id": 4,
                "name": "Мастер обмена",
                "description": "Заверши 5 успешных обменов",
                "progress": 3,
                "required": 5,
                "progress_percentage": 60
            },
            {
                "id": 5, 
                "name": "Отличник",
                "description": "Получи 10 отзывов с оценкой 5",
                "progress": 7,
                "required": 10,
                "progress_percentage": 70
            }
        ]
    }

@router.post("/admin/badges", response_model=BadgeOut, status_code=status.HTTP_201_CREATED)
async def create_badge(
    badge_data: BadgeCreate,
    current_user: User = Depends(get_admin_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Создание нового значка (только для администраторов).
    
    Требуются права администратора.
    """
    from app.models.gamification import Badge, BadgeType

    from sqlalchemy import select
    result = await db.execute(
        select(Badge).where(Badge.type == badge_data.type)
    )
    existing_badge = result.scalar_one_or_none()
    
    if existing_badge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Badge with type {badge_data.type} already exists"
        )
    
    new_badge = Badge(
        name=badge_data.name,
        type=badge_data.type,
        description=badge_data.description,
        icon=badge_data.icon
    )
    
    db.add(new_badge)
    await db.commit()
    await db.refresh(new_badge)
    
    return {
        "id": new_badge.id,
        "name": new_badge.name,
        "type": new_badge.type,
        "description": new_badge.description,
        "icon": new_badge.icon
    }

@router.post("/admin/users/{user_id}/award-badge/{badge_id}", response_model=BadgeAwardResponse)
async def award_badge_to_user(
    user_id: str,
    badge_id: int,
    current_user: User = Depends(get_admin_user),  
    db: AsyncSession = Depends(get_db)
):
    """
    Выдача значка пользователю (только для администраторов).
    """
    from app.models.gamification import Badge
    from app.models.user import User
    from sqlalchemy import select

    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
 
    badge_result = await db.execute(
        select(Badge).where(Badge.id == badge_id)
    )
    badge = badge_result.scalar_one_or_none()
    
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )

    if badge in user.badges:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this badge"
        )
    
    user.badges.append(badge)
    await db.commit()
    
    return {
        "message": "Badge awarded successfully",
        "user_id": user_id,
        "badge_id": badge_id,
        "badge_name": badge.name
    }

@router.get("/admin/stats/detailed", response_model=DetailedStatsOut)
async def get_detailed_gamification_stats(
    current_user: User = Depends(get_admin_user),  
    db: AsyncSession = Depends(get_db)
):
    """
    Получение детальной статистики геймификации (только для администраторов).
    """
    from sqlalchemy import select, func
    from app.models.gamification import Badge
    from app.models.user import User
    
    total_badges_result = await db.execute(select(func.count(Badge.id)))
    total_badges = total_badges_result.scalar()

    users_with_badges_result = await db.execute(
        select(func.count(User.id)).where(User.badges.any())
    )
    users_with_badges = users_with_badges_result.scalar()
    
    
    return {
        "total_badges": total_badges or 0,
        "users_with_badges": users_with_badges or 0,
        "badge_distribution_rate": round((users_with_badges / total_badges) * 100, 2) if total_badges and total_badges > 0 else 0,
        "most_awarded_badges": [
            {"badge_name": "Новичок", "count": 1250},
            {"badge_name": "Первый обмен", "count": 543},
            {"badge_name": "Популярный", "count": 210}
        ]
    }

@router.get("/health")
async def gamification_health():
    """
    Проверка здоровья модуля геймификации.
    """
    return {
        "status": "healthy",
        "module": "gamification",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.get("", include_in_schema=False)
async def gamification_root():
    """Корневой эндпоинт геймификации (скрытый)."""
    return {
        "message": "🎮 Gamification API is working!",
        "available_endpoints": [
            "/api/v1/gamification/test",
            "/api/v1/gamification/reviews", 
            "/api/v1/gamification/profile/{user_id}",
            "/api/v1/gamification/my/profile",
            "/api/v1/gamification/leaderboard",
            "/api/v1/gamification/level-progress",
            "/api/v1/gamification/users/{user_id}/reviews",
            "/api/v1/gamification/badges",
            "/api/v1/gamification/stats/global",
            "/api/v1/gamification/achievements/unlocked",
            "/api/v1/gamification/health"
        ]
    }