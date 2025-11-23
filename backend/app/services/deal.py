from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime

from app.models.deal import Deal, DealStatus, DealStatusLog
from app.models.chat import Chat
from app.models.ad import Ad
from app.schemas.deal import DealCreate, DealUpdate, DealStatusUpdate, DealProposal


class DealService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_deal(self, deal_data: DealCreate, student_id: str) -> Optional[Deal]:
        """Создать сделку для чата"""

        chat_result = await self.db.execute(
            select(Chat).where(Chat.id == deal_data.chat_id)
        )
        chat = chat_result.scalar_one_or_none()
        
        if not chat:
            return None

        existing_deal = await self.get_deal_by_chat_id(deal_data.chat_id)
        if existing_deal:
            return existing_deal

        teacher_id = chat.user1_id if chat.user1_id != student_id else chat.user2_id

        deal = Deal(
            chat_id=deal_data.chat_id,
            student_id=student_id,
            teacher_id=teacher_id,
            proposed_skill=deal_data.proposed_skill,
            proposed_time=deal_data.proposed_time,
            proposed_place=deal_data.proposed_place,
            status=DealStatus.NEW
        )
        
        self.db.add(deal)
        await self.db.commit()
        await self.db.refresh(deal)
        await self._create_status_log(deal, None, DealStatus.NEW, student_id, "Создание сделки")
        
        return deal

    async def get_deal_by_chat_id(self, chat_id: int) -> Optional[Deal]:
        """Получить сделку по ID чата"""
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Deal)
            .options(
                selectinload(Deal.status_logs).selectinload(DealStatusLog.changed_by),
                selectinload(Deal.student),
                selectinload(Deal.teacher)
            )
            .where(Deal.chat_id == chat_id)
        )
        return result.scalar_one_or_none()

    async def update_deal_status(self, deal: Deal, status_update: DealStatusUpdate, user_id: str) -> Optional[Deal]:
        """Обновить статус сделки"""
        old_status = deal.status
        new_status = status_update.status

        if not self._is_valid_status_transition(old_status, new_status):
            return None

        deal.status = new_status
        deal.updated_at = datetime.utcnow()

        await self._create_status_log(deal, old_status, new_status, user_id, status_update.reason)
        
        await self.db.commit()
        await self.db.refresh(deal)
        
        return deal

    async def propose_deal_terms(self, deal: Deal, proposal: DealProposal, user_id: str) -> Optional[Deal]:
        """Предложить условия сделки"""
        if user_id not in [deal.student_id, deal.teacher_id]:
            return None

        deal.proposed_skill = proposal.skill
        deal.proposed_time = proposal.time
        deal.proposed_place = proposal.place

        if deal.status == DealStatus.NEW:
            old_status = deal.status
            deal.status = DealStatus.DISCUSSION
            await self._create_status_log(deal, old_status, DealStatus.DISCUSSION, user_id, "Начало обсуждения условий")
        
        deal.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(deal)
        
        return deal

    async def _create_status_log(self, deal: Deal, old_status: Optional[DealStatus], new_status: DealStatus, user_id: str, reason: Optional[str] = None):
        """Создать запись в логе статусов"""
        status_log = DealStatusLog(
            deal_id=deal.id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=user_id,
            reason=reason
        )
        self.db.add(status_log)

    def _is_valid_status_transition(self, old_status: DealStatus, new_status: DealStatus) -> bool:
        """Проверка валидности перехода между статусами"""
        valid_transitions = {
            DealStatus.NEW: [DealStatus.DISCUSSION, DealStatus.CANCELED],
            DealStatus.DISCUSSION: [DealStatus.CONFIRMED, DealStatus.CANCELED],
            DealStatus.CONFIRMED: [DealStatus.COMPLETED, DealStatus.CANCELED],
            DealStatus.COMPLETED: [],
            DealStatus.CANCELED: []
        }
        
        return new_status in valid_transitions.get(old_status, [])

    async def get_user_deals(self, user_id: str) -> List[Deal]:
        """Получить все сделки пользователя"""
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Deal)
            .options(
                selectinload(Deal.status_logs).selectinload(DealStatusLog.changed_by),
                selectinload(Deal.student),
                selectinload(Deal.teacher),
                selectinload(Deal.chat)
            )
            .where(
                and_(
                    Deal.status != DealStatus.CANCELED,
                    (Deal.student_id == user_id) | (Deal.teacher_id == user_id)
                )
            )
            .order_by(Deal.updated_at.desc())
        )
        return result.scalars().all()


async def complete_deal(self, deal: Deal, user_id: str) -> Optional[Deal]:
    """Завершение сделки с обновлением статистики."""
    from app.services.gamification import GamificationService
    
    old_status = deal.status
    new_status = DealStatus.COMPLETED
    
    if not self._is_valid_status_transition(old_status, new_status):
        return None
    
    deal.status = new_status
    deal.updated_at = datetime.utcnow()

    await self._create_status_log(deal, old_status, new_status, user_id, "Сделка завершена")
    
    gamification_service = GamificationService(self.db)
 
    chat_result = await self.db.execute(
        select(Chat).where(Chat.id == deal.chat_id)
    )
    chat = chat_result.scalar_one_or_none()
    
    if chat and chat.ad:
    
        await gamification_service.update_stats_after_exchange(
            deal.student_id, chat.ad.category
        )
        await gamification_service.update_stats_after_exchange(
            deal.teacher_id, chat.ad.category
        )
    
    await self.db.commit()
    await self.db.refresh(deal)
    
    return deal