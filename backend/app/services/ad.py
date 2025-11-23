from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, Tuple
import math

from app.models.ad import Ad
from app.models.user import User
from app.schemas.ad import AdCreate, AdUpdate, AdFilter

class AdService:
    """Сервис для работы с объявлениями."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ad(self, ad_data: AdCreate, author_id: str) -> Ad:
        """Создание нового объявления."""
        active_ads_count = await self._get_user_active_ads_count(author_id)
        if active_ads_count >= 20:
            raise ValueError("User cannot have more than 20 active ads")

        new_ad = Ad(
            **ad_data.model_dump(),
            author_id=author_id
        )
        
        self.db.add(new_ad)
        await self.db.commit()
        await self.db.refresh(new_ad)

        await self.db.refresh(new_ad, ['author'])
        if new_ad.author and new_ad.author.profile:
            await self.db.refresh(new_ad.author.profile)
            
        return new_ad

    async def get_ad_by_id(self, ad_id: str) -> Optional[Ad]:
        """Получение объявления по ID."""
        result = await self.db.execute(
            select(Ad)
            .options(selectinload(Ad.author).selectinload(User.profile))
            .where(Ad.id == ad_id)
        )
        return result.scalar_one_or_none()

    async def update_ad(self, ad: Ad, update_data: AdUpdate) -> Ad:
        """Обновление объявления."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(ad, field, value)
        
        await self.db.commit()
        await self.db.refresh(ad)
        return ad

    async def delete_ad(self, ad: Ad) -> None:
        """Полноценное удаление объявления из базы данных."""
        await self.db.delete(ad)
        await self.db.commit()

    async def get_ads_with_filters(self, filters: AdFilter) -> Tuple[list[Ad], int]:
        """Получение списка объявлений с фильтрами и пагинацией."""

        query = select(Ad)
        query = query.options(selectinload(Ad.author).selectinload(User.profile))
        if filters.category:
            query = query.where(Ad.category == filters.category)
        if filters.level:
            query = query.where(Ad.level == filters.level)
        if filters.format:
            query = query.where(Ad.format == filters.format)

        if filters.q:
            search_term = f"%{filters.q}%"
            query = query.where(
                or_(
                    Ad.title.ilike(search_term),
                    Ad.description.ilike(search_term)
                )
            )

        if filters.sort == "newest":
            query = query.order_by(Ad.created_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        result = await self.db.execute(query)
        ads = result.scalars().all()

        return ads, total

    async def _get_user_active_ads_count(self, user_id: str) -> int:
        """Получение количества активных объявлений пользователя."""
        result = await self.db.execute(
            select(func.count(Ad.id)).where(Ad.author_id == user_id)
        )
        return result.scalar()

    async def is_ad_owner(self, ad_id: str, user_id: str) -> bool:
        """Проверка, является ли пользователь владельцем объявления."""
        result = await self.db.execute(
            select(Ad).where(Ad.id == ad_id, Ad.author_id == user_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_user_ads(self, user_id: str) -> list[Ad]:
        """Получение всех объявлений пользователя."""
        result = await self.db.execute(
            select(Ad)
            .options(selectinload(Ad.author).selectinload(User.profile))
            .where(Ad.author_id == user_id)
            .order_by(Ad.created_at.desc())
        )
        return result.scalars().all()