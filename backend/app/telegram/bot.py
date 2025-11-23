import logging
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        if self.token:
            self.base_url = f"https://api.telegram.org/bot{self.token}"
        else:
            self.base_url = None
        self._user_chat_ids = {}
        self.is_running = False
        
    async def start(self):
        """Запуск бота в фоновом режиме"""
        if not self.token:
            logger.warning("⏭️ Telegram bot disabled - TELEGRAM_BOT_TOKEN not set")
            return
            
        self.is_running = True
        logger.info("🤖 Simple Telegram Bot started (HTTP API mode)")

        asyncio.create_task(self._poll_updates())
    
    async def stop(self):
        """Остановка бота"""
        self.is_running = False
        logger.info("🤖 Simple Telegram Bot stopped")
    
    async def _poll_updates(self):
        """Фоновая задача для опроса обновлений"""
        offset = 0
        while self.is_running:
            try:
                updates = await self._get_updates(offset)
                for update in updates:
                    await self._process_update(update)
                    offset = update['update_id'] + 1
            except Exception as e:
                logger.error(f"Error polling updates: {e}")
            
            await asyncio.sleep(1)
    
    async def _get_updates(self, offset=0):
        """Получить обновления от Telegram"""
        if not self.token:
            return []
            
        import httpx
        
        url = f"{self.base_url}/getUpdates"
        params = {
            "offset": offset,
            "timeout": 10,  
            "limit": 100
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('ok'):
                        logger.error(f"❌ Telegram API error: {data}")
                        return []
                    
                    updates = data.get('result', [])
                    if updates:
                        logger.info(f"✅ Received {len(updates)} updates")
                    return updates
                else:
                    logger.error(f"❌ HTTP error {response.status_code}: {response.text}")
                    return []
        except httpx.ConnectTimeout:
            logger.debug("⏱️  Connection timeout (normal for polling)")
            return []
        except httpx.ConnectError as e:
            logger.error(f"❌ Connection error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return []
    
    async def _process_update(self, update):
        """Обработать входящее обновление"""
        if 'message' in update and 'text' in update['message']:
            message = update['message']
            chat_id = message['chat']['id']
            text = message['text']
            
            if text.startswith('/start'):
                await self._send_welcome(chat_id)
            elif text.startswith('/help'):
                await self._send_help(chat_id)
            elif text in ['/id', '/chatid']:
                await self._send_chat_id(chat_id)
    
    async def _send_welcome(self, chat_id):
        """Отправить приветственное сообщение"""
        message = (
            "👋 **Добро пожаловать в SkillSwap Notifications!**\n\n"
            "🤖 **Это бот для уведомлений от платформы обмена знаниями SkillSwap**\n\n"
            "📋 **Чтобы начать получать уведомления:**\n"
            "1. Перейдите в настройки профиля на сайте SkillSwap\n"
            "2. Найдите раздел 'Telegram уведомления'\n" 
            "3. Вставьте ваш Chat ID в форму подписки\n"
            "4. Нажмите 'Подписаться'\n\n"
            "✅ **После подписки вы будете получать:**\n"
            "• 🔐 Коды подтверждения по SMS\n"
            "• 💬 Уведомления о новых сообщениях\n"
            "• 🤝 Обновления по сделкам\n"
            "• 📢 Важные объявления\n"
            "• 🏆 Достижения и бейджи\n\n"
            f"🆔 **Ваш Chat ID:** `{chat_id}`\n\n"
            "📋 **Скопируйте этот ID и используйте его на сайте!**\n\n"
            "💡 **Команды:** /help - справка, /id - показать Chat ID"
        )
        
        await self._send_message(chat_id, message)
    
    async def _send_help(self, chat_id):
        """Отправить справку"""
        message = (
            "🤖 **SkillSwap Notifications Bot**\n\n"
            "📋 **Доступные команды:**\n"
            "/start - Начать работу и получить Chat ID\n"
            "/help - Показать эту справку\n"
            "/id - Показать ваш Chat ID\n\n"
            f"💡 **Ваш Chat ID:** `{chat_id}`\n\n"
            "❓ **Как подписаться на уведомления?**\n"
            "1. Скопируйте ваш Chat ID выше\n"
            "2. Перейдите в настройки профиля на сайте SkillSwap\n"
            "3. Вставьте Chat ID в форму подписки\n"
            "4. Нажмите 'Подписаться'\n"
            "5. Вы получите тестовое уведомление для подтверждения"
        )
        
        await self._send_message(chat_id, message)
    
    async def _send_chat_id(self, chat_id):
        """Отправить Chat ID"""
        await self._send_message(
            chat_id,
            f"🆔 **Ваш Chat ID:** `{chat_id}`\n\n"
            "Скопируйте этот номер и вставьте в форму на сайте SkillSwap"
        )
    
    async def send_message(self, chat_id, text, parse_mode="Markdown"):
        """Отправить сообщение (публичный метод для других сервисов)"""
        return await self._send_message(chat_id, text, parse_mode)
    
    async def _send_message(self, chat_id, text, parse_mode="Markdown"):
        """Отправить сообщение через HTTP API"""
        if not self.token:
            logger.warning("Cannot send message - TELEGRAM_BOT_TOKEN not set")
            return False
            
        import httpx
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    logger.info(f"📨 Message sent to {chat_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send message to {chat_id}: {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return False
    
    def subscribe_user(self, user_id, chat_id):
        """Подписать пользователя на уведомления"""
        self._user_chat_ids[user_id] = chat_id
        logger.info(f"✅ User {user_id} subscribed with chat_id {chat_id}")
    
    def unsubscribe_user(self, user_id):
        """Отписать пользователя от уведомлений"""
        if user_id in self._user_chat_ids:
            del self._user_chat_ids[user_id]
            logger.info(f"✅ User {user_id} unsubscribed")
    
    def is_subscribed(self, user_id):
        """Проверить подписку пользователя"""
        return user_id in self._user_chat_ids
    
    def get_chat_id(self, user_id):
        """Получить chat_id пользователя"""
        return self._user_chat_ids.get(user_id)

telegram_bot_instance = SimpleTelegramBot()