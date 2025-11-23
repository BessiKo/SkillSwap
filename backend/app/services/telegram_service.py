import logging
from typing import Dict, List, Optional
import json
from app.config import settings
from app.database import get_redis

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.redis_key_prefix = "telegram:subscription:"
    
    def _get_user_key(self, user_id: int) -> str:
        """Генерация ключа Redis для пользователя"""
        return f"{self.redis_key_prefix}{user_id}"
    
    async def subscribe_user(self, user_id: int, chat_id: str):
        """Подписка пользователя на уведомления"""
        redis_client = await get_redis()
        
        subscription_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "subscribed_at": self._get_current_timestamp()
        }
        
        await redis_client.set(
            self._get_user_key(user_id),
            json.dumps(subscription_data),
            ex=60*60*24*30 
        )
        
        logger.info(f"User {user_id} subscribed to Telegram notifications with chat_id {chat_id}")
    
    async def unsubscribe_user(self, user_id: int):
        """Отписка пользователя от уведомлений"""
        redis_client = await get_redis()
        await redis_client.delete(self._get_user_key(user_id))
        logger.info(f"User {user_id} unsubscribed from Telegram notifications")
    
    async def is_subscribed(self, user_id: int) -> bool:
        """Проверка подписки пользователя"""
        redis_client = await get_redis()
        subscription = await redis_client.get(self._get_user_key(user_id))
        return subscription is not None
    
    async def get_chat_id(self, user_id: int) -> Optional[str]:
        """Получение chat_id пользователя"""
        redis_client = await get_redis()
        subscription_data = await redis_client.get(self._get_user_key(user_id))
        
        if subscription_data:
            data = json.loads(subscription_data)
            return data.get("chat_id")
        return None
    
    async def get_subscription_info(self, user_id: int) -> Optional[dict]:
        """Получение полной информации о подписке"""
        redis_client = await get_redis()
        subscription_data = await redis_client.get(self._get_user_key(user_id))
        
        if subscription_data:
            return json.loads(subscription_data)
        return None
    
    async def send_message(self, chat_id: str, message: str, parse_mode: str = "Markdown") -> bool:
        """Отправка сообщения пользователю через бота"""
        from app.telegram.bot import telegram_bot_instance
        return await telegram_bot_instance.send_message(chat_id, message, parse_mode)
    
    async def send_sms_code(self, user_id: int, phone: str, code: str):
        """Отправка SMS кода через телеграм"""
        if await self.is_subscribed(user_id):
            chat_id = await self.get_chat_id(user_id)
            if chat_id:
                message = f"🔐 **Код подтверждения**\nДля номера: `{phone}`\n\nВаш код: `{code}`"
                return await self.send_message(chat_id, message)
        return False
    
    async def send_new_message_notification(self, user_id: int, from_user: str, message_preview: str):
        """Уведомление о новом сообщении"""
        if await self.is_subscribed(user_id):
            chat_id = await self.get_chat_id(user_id)
            if chat_id:
                message = (
                    f"💬 **Новое сообщение**\n"
                    f"От: **{from_user}**\n"
                    f"Сообщение: _{message_preview[:100]}..._"
                )
                return await self.send_message(chat_id, message)
        return False
    
    async def send_deal_notification(self, user_id: int, deal_type: str, details: str):
        """Уведомление о сделке"""
        if await self.is_subscribed(user_id):
            chat_id = await self.get_chat_id(user_id)
            if chat_id:
                message = f"🤝 **{deal_type}**\n{details}"
                return await self.send_message(chat_id, message)
        return False
    
    async def send_announcement(self, user_id: int, title: str, content: str):
        """Отправка объявления"""
        if await self.is_subscribed(user_id):
            chat_id = await self.get_chat_id(user_id)
            if chat_id:
                message = f"📢 **{title}**\n\n{content}"
                return await self.send_message(chat_id, message)
        return False
    
    async def send_gamification_notification(self, user_id: int, achievement: str, points: int):
        """Уведомление о геймификации"""
        if await self.is_subscribed(user_id):
            chat_id = await self.get_chat_id(user_id)
            if chat_id:
                message = f"🏆 **Новое достижение!**\n{achievement}\n🎯 +{points} очков!"
                return await self.send_message(chat_id, message)
        return False
    
    async def get_all_subscriptions(self) -> List[dict]:
        """Получение всех подписок (для админки)"""
        redis_client = await get_redis()
        keys = await redis_client.keys(f"{self.redis_key_prefix}*")
        subscriptions = []
        
        for key in keys:
            data = await redis_client.get(key)
            if data:
                subscriptions.append(json.loads(data))
        
        return subscriptions
    
    async def get_subscriptions_count(self) -> int:
        """Получение количества подписок"""
        redis_client = await get_redis()
        keys = await redis_client.keys(f"{self.redis_key_prefix}*")
        return len(keys)
    
    def _get_current_timestamp(self) -> str:
        """Получение текущего времени в строковом формате"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

telegram_service = TelegramService()