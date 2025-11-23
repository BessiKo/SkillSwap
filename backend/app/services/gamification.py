# app/services/gamification.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict
import math

from app.models.gamification import Review, UserStats, BadgeType
from app.models.user import User, UserProfile, Badge
from app.models.deal import Deal, DealStatus
from app.models.ad import Ad, AdCategory
from app.schemas.gamification import ReviewCreate

class GamificationService:
    """Сервис для работы с геймификацией."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.EXP_PER_LEVEL = 100  
        self.REPUTATION_PER_EXCHANGE = 10  
        self.LEVEL_CAPS = { 
            "exchanges": [5, 10, 25, 50, 100],
            "rating": [4.0, 4.5, 4.8, 4.9, 5.0]
        }

    async def create_review(self, review_data: ReviewCreate, author_id: str) -> Review:
        """Создание отзыва и обновление статистики."""
        deal_result = await self.db.execute(
            select(Deal).where(
                and_(
                    Deal.id == review_data.deal_id,
                    or_(Deal.student_id == author_id, Deal.teacher_id == author_id),
                    Deal.status == DealStatus.COMPLETED
                )
            )
        )
        deal = deal_result.scalar_one_or_none()
        
        if not deal:
            raise ValueError("Deal not found or not completed")

        existing_review = await self.db.execute(
            select(Review).where(
                and_(
                    Review.deal_id == review_data.deal_id,
                    Review.author_id == author_id
                )
            )
        )
        if existing_review.scalar_one_or_none():
            raise ValueError("Review already exists for this deal")

        review = Review(
            **review_data.model_dump(),
            author_id=author_id
        )
        self.db.add(review)

        await self._update_user_stats_after_review(review_data.target_user_id, review_data.rating)

        await self._check_and_award_badges(review_data.target_user_id)
        
        await self.db.commit()
        await self.db.refresh(review)
        
        return review

    async def _update_user_stats_after_review(self, user_id: str, rating: int):
        """Обновление статистики пользователя после отзыва."""

        stats_result = await self.db.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = stats_result.scalar_one_or_none()
        
        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)

        total_ratings = stats.total_ratings
        current_avg = stats.average_rating
        
        new_total = total_ratings + 1
        new_avg = (current_avg * total_ratings + rating) / new_total
        
        stats.total_ratings = new_total
        stats.average_rating = round(new_avg, 2)

        stats.reputation += rating * 2

    async def update_stats_after_exchange(self, user_id: str, category: AdCategory):
        """Обновление статистики после завершенного обмена."""
        stats_result = await self.db.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = stats_result.scalar_one_or_none()
        
        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)

        stats.exchanges_completed += 1
        stats.reputation += self.REPUTATION_PER_EXCHANGE

        category_field = f"{category.value}_exchanges"
        if hasattr(stats, category_field):
            current_value = getattr(stats, category_field)
            setattr(stats, category_field, current_value + 1)

        await self._update_level_and_experience(stats)

        await self._check_and_award_badges(user_id)
        
        await self.db.commit()

    async def _update_level_and_experience(self, stats: UserStats):
        """Обновление уровня и опыта пользователя."""

        stats.experience += 10

        required_exp = stats.level * self.EXP_PER_LEVEL
        while stats.experience >= required_exp:
            stats.experience -= required_exp
            stats.level += 1
            required_exp = stats.level * self.EXP_PER_LEVEL

    async def _check_and_award_badges(self, user_id: str):
        """Проверка и выдача значков пользователю."""
        stats_result = await self.db.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = stats_result.scalar_one_or_none()
        
        if not stats:
            return
        
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return

        current_badge_types = {badge.type for badge in user.badges}
        new_badges = []

        badges_to_check = {
            BadgeType.FIRST_EXCHANGE: stats.exchanges_completed >= 1,
            BadgeType.POPULAR: stats.exchanges_completed >= 10,
            BadgeType.MENTOR: stats.exchanges_completed >= 25,
            BadgeType.EXPERT: stats.exchanges_completed >= 50,
            BadgeType.TOP_RATED: stats.average_rating >= 4.8 and stats.total_ratings >= 5,
        }
        
        for badge_type, condition in badges_to_check.items():
            if condition and badge_type not in current_badge_types:

                badge_result = await self.db.execute(
                    select(Badge).where(Badge.type == badge_type)
                )
                badge = badge_result.scalar_one_or_none()
                
                if badge:
                    user.badges.append(badge)
                    new_badges.append(badge)
        
        category_fields = {
            'programming': BadgeType.CATEGORY_EXPERT,
            'design': BadgeType.CATEGORY_EXPERT,
            'languages': BadgeType.CATEGORY_EXPERT,
            'math': BadgeType.CATEGORY_EXPERT,
            'science': BadgeType.CATEGORY_EXPERT,
            'business': BadgeType.CATEGORY_EXPERT,
            'music': BadgeType.CATEGORY_EXPERT,
            'sports': BadgeType.CATEGORY_EXPERT,
            'other': BadgeType.CATEGORY_EXPERT,
        }
        
        for category_field, badge_type in category_fields.items():
            exchanges = getattr(stats, f"{category_field}_exchanges", 0)
            if exchanges >= 10 and badge_type not in current_badge_types:
                badge_result = await self.db.execute(
                    select(Badge).where(Badge.type == badge_type)
                )
                badge = badge_result.scalar_one_or_none()
                
                if badge:
                    user.badges.append(badge)
                    new_badges.append(badge)

    async def get_user_profile_with_gamification(self, user_id: str) -> Dict:
        """Получение профиля пользователя с геймификацией."""
        from sqlalchemy.orm import selectinload
        
        user_result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.stats),
                selectinload(User.badges)
            )
            .where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user or not user.profile:
            raise ValueError("User or profile not found")
      
        reviews_result = await self.db.execute(
            select(Review)
            .options(selectinload(Review.author).selectinload(User.profile))
            .where(Review.target_user_id == user_id)
            .order_by(Review.created_at.desc())
            .limit(10)
        )
        reviews = reviews_result.scalars().all()

        profile_data = {
            "id": user.id,
            "first_name": user.profile.first_name,
            "last_name": user.profile.last_name,
            "avatar_url": user.profile.avatar_url,
            "university": user.profile.university,
            "faculty": user.profile.faculty,
            "year": user.profile.year,
            "bio": user.profile.bio,
            "stats": {
                "reputation": user.stats.reputation if user.stats else 0,
                "exchanges_completed": user.stats.exchanges_completed if user.stats else 0,
                "total_ratings": user.stats.total_ratings if user.stats else 0,
                "average_rating": user.stats.average_rating if user.stats else 0.0,
                "level": user.stats.level if user.stats else 1,
                "experience": user.stats.experience if user.stats else 0,
                "next_level_exp": (user.stats.level * self.EXP_PER_LEVEL) if user.stats else self.EXP_PER_LEVEL,
                "programming_exchanges": user.stats.programming_exchanges if user.stats else 0,
                "design_exchanges": user.stats.design_exchanges if user.stats else 0,
                "languages_exchanges": user.stats.languages_exchanges if user.stats else 0,
                "math_exchanges": user.stats.math_exchanges if user.stats else 0,
                "science_exchanges": user.stats.science_exchanges if user.stats else 0,
                "business_exchanges": user.stats.business_exchanges if user.stats else 0,
                "music_exchanges": user.stats.music_exchanges if user.stats else 0,
                "sports_exchanges": user.stats.sports_exchanges if user.stats else 0,
                "other_exchanges": user.stats.other_exchanges if user.stats else 0,
            } if user.stats else {},
            "badges": [{
                "id": badge.id,
                "name": badge.name,
                "type": badge.type,
                "description": badge.description,
                "icon": badge.icon
            } for badge in user.badges],
            "reviews": [{
                "id": review.id,
                "author_id": review.author_id,
                "target_user_id": review.target_user_id,
                "deal_id": review.deal_id,
                "rating": review.rating,
                "text": review.text,
                "created_at": review.created_at,
                "author_name": f"{review.author.profile.first_name} {review.author.profile.last_name}",
                "author_avatar": review.author.profile.avatar_url
            } for review in reviews]
        }
        
        return profile_data

    async def get_leaderboard(self, limit: int = 50) -> List[Dict]:
        """Получение таблицы лидеров."""
        result = await self.db.execute(
            select(User, UserProfile, UserStats)
            .join(UserProfile, User.id == UserProfile.user_id)
            .join(UserStats, User.id == UserStats.user_id)
            .where(User.is_active == True)
            .order_by(UserStats.reputation.desc())
            .limit(limit)
        )
        
        leaderboard = []
        for position, (user, profile, stats) in enumerate(result.all(), 1):
            leaderboard.append({
                "id": user.id,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "avatar_url": profile.avatar_url,
                "university": profile.university,
                "reputation": stats.reputation,
                "level": stats.level,
                "position": position
            })
        
        return leaderboard

    async def get_level_progress(self, user_id: str) -> Dict:
        """Получение прогресса уровня пользователя."""
        stats_result = await self.db.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = stats_result.scalar_one_or_none()
        
        if not stats:
            return {
                "current_level": 1,
                "current_exp": 0,
                "next_level_exp": self.EXP_PER_LEVEL,
                "progress_percentage": 0.0
            }
        
        next_level_exp = stats.level * self.EXP_PER_LEVEL
        progress_percentage = (stats.experience / next_level_exp) * 100
        
        return {
            "current_level": stats.level,
            "current_exp": stats.experience,
            "next_level_exp": next_level_exp,
            "progress_percentage": round(progress_percentage, 2)
        }