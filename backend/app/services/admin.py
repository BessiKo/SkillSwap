from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, Tuple, List
import math

from app.models.user import User, UserRole, UserProfile
from app.models.ad import Ad
from app.models.chat import Chat, Message
from app.models.deal import Deal, DealStatus
from app.models.admin import AdminLog, AdminActionType
from app.schemas.admin import UserBanRequest, AdminActionRequest

class AdminService:
    """Сервис для работы с админ-панелью."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users_list(
        self, 
        page: int = 1, 
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """Получение списка пользователей с фильтрами."""
        query = select(User).options(selectinload(User.profile))
        
        if search:
            search_term = f"%{search}%"
            query = query.join(User.profile).where(
                or_(
                    User.phone.ilike(search_term),
                    UserProfile.first_name.ilike(search_term),
                    UserProfile.last_name.ilike(search_term)
                )
            )
        
        if role:
            query = query.where(User.role == role)
            
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.order_by(desc(User.created_at)).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return users, total

    async def get_ads_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        author_id: Optional[str] = None
    ) -> Tuple[List[Ad], int]:
        """Получение списка объявлений для админ-панели."""
        query = select(Ad).options(
            selectinload(Ad.author).selectinload(User.profile)
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Ad.title.ilike(search_term),
                    Ad.description.ilike(search_term)
                )
            )
        
        if category:
            query = query.where(Ad.category == category)
            
        if author_id:
            query = query.where(Ad.author_id == author_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.order_by(desc(Ad.created_at)).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        ads = result.scalars().all()
        
        return ads, total

    async def get_chats_list(
        self,
        page: int = 1,
        page_size: int = 20,
        ad_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[List[Chat], int]:
        """Получение списка чатов для админ-панели."""
        query = select(Chat).options(
            selectinload(Chat.ad).selectinload(Ad.author).selectinload(User.profile),
            selectinload(Chat.user1).selectinload(User.profile),
            selectinload(Chat.user2).selectinload(User.profile),
            selectinload(Chat.messages).selectinload(Message.sender).selectinload(User.profile),
            selectinload(Chat.deal)
        )
        
        if ad_id:
            query = query.where(Chat.ad_id == ad_id)
            
        if user_id:
            query = query.where(
                or_(Chat.user1_id == user_id, Chat.user2_id == user_id)
            )
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.order_by(desc(Chat.created_at)).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        chats = result.scalars().all()
        
        return chats, total

    async def get_deals_list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[DealStatus] = None,
        user_id: Optional[str] = None
    ) -> Tuple[List[Deal], int]:
        """Получение списка сделок для админ-панели."""
        query = select(Deal).options(
            selectinload(Deal.chat).selectinload(Chat.ad),
            selectinload(Deal.student).selectinload(User.profile),
            selectinload(Deal.teacher).selectinload(User.profile),
            selectinload(Deal.status_logs)
        )
        
        if status:
            query = query.where(Deal.status == status)
            
        if user_id:
            query = query.where(
                or_(Deal.student_id == user_id, Deal.teacher_id == user_id)
            )
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.order_by(desc(Deal.created_at)).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        deals = result.scalars().all()
        
        return deals, total

    async def get_chat_messages(self, chat_id: int) -> List[Message]:
        """Получение сообщений чата."""
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.sender).selectinload(User.profile))
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    async def ban_user(
        self, 
        user_id: str, 
        admin_id: str, 
        ban_data: UserBanRequest
    ) -> User:
        """Блокировка пользователя."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        if user.role == UserRole.ADMIN:
            raise ValueError("Cannot ban admin user")
        
        user.is_active = False
        
        admin_log = AdminLog(
            admin_id=admin_id,
            action_type=AdminActionType.USER_BANNED,
            target_user_id=user_id,
            reason=ban_data.reason,
            details=ban_data.details
        )
        self.db.add(admin_log)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user

    async def unban_user(
        self, 
        user_id: str, 
        admin_id: str, 
        unban_data: AdminActionRequest
    ) -> User:
        """Разблокировка пользователя."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        user.is_active = True
        
        admin_log = AdminLog(
            admin_id=admin_id,
            action_type=AdminActionType.USER_UNBANNED,
            target_user_id=user_id,
            reason=unban_data.reason,
            details=unban_data.details
        )
        self.db.add(admin_log)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user

    async def delete_ad(
        self, 
        ad_id: str, 
        admin_id: str, 
        delete_data: AdminActionRequest
    ) -> None:
        """Удаление объявления администратором."""
        result = await self.db.execute(
            select(Ad).where(Ad.id == ad_id)
        )
        ad = result.scalar_one_or_none()
        
        if not ad:
            raise ValueError("Ad not found")
        
        admin_log = AdminLog(
            admin_id=admin_id,
            action_type=AdminActionType.AD_DELETED,
            target_ad_id=ad_id,
            reason=delete_data.reason,
            details=delete_data.details
        )
        self.db.add(admin_log)
        
        await self.db.delete(ad)
        await self.db.commit()

    async def delete_chat(
        self, 
        chat_id: int, 
        admin_id: str, 
        delete_data: AdminActionRequest
    ) -> None:
        """Удаление чата администратором."""
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        chat = result.scalar_one_or_none()
        
        if not chat:
            raise ValueError("Chat not found")
        
        admin_log = AdminLog(
            admin_id=admin_id,
            action_type=AdminActionType.CHAT_DELETED,
            target_chat_id=chat_id,
            reason=delete_data.reason,
            details=delete_data.details
        )
        self.db.add(admin_log)
        
        await self.db.delete(chat)
        await self.db.commit()

    async def cancel_deal(
        self, 
        deal_id: int, 
        admin_id: str, 
        cancel_data: AdminActionRequest
    ) -> Deal:
        """Отмена сделки администратором."""
        result = await self.db.execute(
            select(Deal).where(Deal.id == deal_id)
        )
        deal = result.scalar_one_or_none()
        
        if not deal:
            raise ValueError("Deal not found")
        
        deal.status = DealStatus.CANCELED
        
        admin_log = AdminLog(
            admin_id=admin_id,
            action_type=AdminActionType.DEAL_CANCELLED,
            target_deal_id=deal_id,
            reason=cancel_data.reason,
            details=cancel_data.details
        )
        self.db.add(admin_log)
        
        await self.db.commit()
        await self.db.refresh(deal)
        
        return deal

    async def get_admin_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        action_type: Optional[AdminActionType] = None,
        admin_id: Optional[str] = None
    ) -> Tuple[List[AdminLog], int]:
        """Получение логов административных действий."""
        query = select(AdminLog).options(
            selectinload(AdminLog.admin).selectinload(User.profile),
            selectinload(AdminLog.target_user).selectinload(User.profile),
            selectinload(AdminLog.target_ad),
            selectinload(AdminLog.target_chat),
            selectinload(AdminLog.target_deal)
        )
        
        if action_type:
            query = query.where(AdminLog.action_type == action_type)
            
        if admin_id:
            query = query.where(AdminLog.admin_id == admin_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.order_by(desc(AdminLog.created_at)).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return logs, total

    async def get_admin_stats(self) -> dict:
        """Получение статистики для админ-панели."""
        total_users_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar()
        
        active_users_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar()
        
        banned_users_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == False)
        )
        banned_users = banned_users_result.scalar()

        total_ads_result = await self.db.execute(select(func.count(Ad.id)))
        total_ads = total_ads_result.scalar()

        total_chats_result = await self.db.execute(select(func.count(Chat.id)))
        total_chats = total_chats_result.scalar()

        total_deals_result = await self.db.execute(select(func.count(Deal.id)))
        total_deals = total_deals_result.scalar()
        
        recent_logs_result = await self.db.execute(
            select(AdminLog)
            .options(
                selectinload(AdminLog.admin).selectinload(User.profile),
                selectinload(AdminLog.target_user).selectinload(User.profile)
            )
            .order_by(desc(AdminLog.created_at))
            .limit(10)
        )
        recent_logs = recent_logs_result.scalars().all()
        
        return {
            "total_users": total_users,
            "total_ads": total_ads,
            "total_chats": total_chats,
            "total_deals": total_deals,
            "active_users": active_users,
            "active_ads": total_ads,
            "banned_users": banned_users,
            "recent_actions": recent_logs
        }