# app/services/chat.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

from app.models.chat import Chat, Message
from app.models.ad import Ad
from app.schemas.chat import ChatCreate, MessageCreate


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat_data: ChatCreate, current_user_id: str) -> Optional[Chat]:  
        """Создать чат при отклике на объявление"""
        ad_result = await self.db.execute(select(Ad).where(Ad.id == chat_data.ad_id))
        ad = ad_result.scalar_one_or_none()
        
        if not ad:
            return None
        

        if ad.author_id == current_user_id:  
            return None

        existing_chat = await self.get_chat_by_ad_and_users(
            chat_data.ad_id, ad.author_id, current_user_id  
        )
        
        if existing_chat:
            return existing_chat
        
        chat = Chat(
            ad_id=chat_data.ad_id,
            user1_id=ad.author_id, 
            user2_id=current_user_id  
        )
        
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        
        return chat

    async def get_chat_by_ad_and_users(self, ad_id: str, user1_id: str, user2_id: str) -> Optional[Chat]: 
        """Найти чат по объявлению и участникам"""
        result = await self.db.execute(
            select(Chat).where(
                and_(
                    Chat.ad_id == ad_id,
                    or_(
                        and_(Chat.user1_id == user1_id, Chat.user2_id == user2_id),
                        and_(Chat.user1_id == user2_id, Chat.user2_id == user1_id)
                    )
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_chats(self, user_id: str) -> List[Chat]:  
        """Получить все чаты пользователя"""
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.user1), selectinload(Chat.user2), selectinload(Chat.ad))
            .where(or_(Chat.user1_id == user_id, Chat.user2_id == user_id))
            .order_by(Chat.created_at.desc())
        )
        return result.scalars().all()

    async def get_chat(self, chat_id: int, user_id: str) -> Optional[Chat]:  
        """Получить чат по ID с проверкой прав доступа"""
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.user1), selectinload(Chat.user2), selectinload(Chat.ad))
            .where(and_(Chat.id == chat_id, or_(Chat.user1_id == user_id, Chat.user2_id == user_id)))
        )
        return result.scalar_one_or_none()

    async def create_message(self, message_data: MessageCreate, sender_id: str) -> Optional[Message]:  
        """Создать сообщение в чате"""

        chat = await self.get_chat(message_data.chat_id, sender_id)
        if not chat:
            return None
        
        message = Message(
            chat_id=message_data.chat_id,
            sender_id=sender_id,
            text=message_data.text
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        return message

    async def get_chat_messages(self, chat_id: int, user_id: str, limit: int = 50, offset: int = 0) -> List[Message]:  
        """Получить сообщения чата с пагинацией"""

        chat = await self.get_chat(chat_id, user_id)
        if not chat:
            return []
        
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def mark_messages_as_read(self, chat_id: int, user_id: str): 
        """Пометить сообщения как прочитанные"""

        result = await self.db.execute(
            select(Message)
            .where(
                and_(
                    Message.chat_id == chat_id,
                    Message.sender_id != user_id,
                    Message.read_at.is_(None)
                )
            )
        )
        messages = result.scalars().all()
        
        for message in messages:
            message.read_at = datetime.utcnow()
        
        if messages:
            await self.db.commit()