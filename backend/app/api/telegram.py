from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.services.telegram_service import telegram_service
from app.schemas.telegram import TelegramSubscribe
from app.config import settings

router = APIRouter()

@router.post("/subscribe", summary="Подписаться на Telegram уведомления")
async def subscribe_to_telegram(
    subscription: TelegramSubscribe,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Подписка на Telegram уведомления
    
    - **chat_id**: ID чата с ботом (пользователь получает его после старта с ботом)
    """
    await telegram_service.subscribe_user(current_user.id, subscription.chat_id)
    
    success = await telegram_service.send_message(
        subscription.chat_id,
        "✅ **Вы успешно подписались на уведомления!**\n\n"
        "Теперь вы будете получать:\n"
        "• Коды подтверждения\n"
        "• Уведомления о сообщениях\n"
        "• Обновления по сделкам\n"
        "• Объявления и новости\n\n"
        "📱 *SkillSwap Notifications*"
    )
    
    return {
        "status": "success" if success else "warning",
        "message": "Подписка оформлена" if success else "Подписка оформлена, но тестовое сообщение не доставлено",
        "user_id": current_user.id,
        "chat_id": subscription.chat_id
    }

@router.post("/unsubscribe", summary="Отписаться от Telegram уведомлений")
async def unsubscribe_from_telegram(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отписка от Telegram уведомлений"""
    await telegram_service.unsubscribe_user(current_user.id)
    
    return {
        "status": "success",
        "message": "Вы отписались от уведомлений",
        "user_id": current_user.id
    }

@router.get("/status", summary="Статус подписки на Telegram уведомления")
async def get_telegram_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверка статуса подписки на Telegram уведомления"""
    is_subscribed = await telegram_service.is_subscribed(current_user.id)
    
    return {
        "is_subscribed": is_subscribed,
        "user_id": current_user.id
    }

@router.get("/bot-info", summary="Получить информацию о боте для ссылки")
async def get_bot_info():
    """Получить информацию о боте (username, ссылка для подписки)"""
    bot_username = "SkillSwapNotifierBot"
    bot_url = f"https://t.me/{bot_username}"
    
    return {
        "bot_username": bot_username,
        "bot_url": bot_url,
        "instructions": "Нажмите на ссылку, затем кнопку START в боте, и вернитесь сюда чтобы подписаться",
        "enabled": True
    }

@router.get("/test-notification", summary="Тестовое уведомление")
async def send_test_notification(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка тестового уведомления"""
    if not await telegram_service.is_subscribed(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не подписаны на уведомления"
        )
    
    chat_id = await telegram_service.get_chat_id(current_user.id)
    success = await telegram_service.send_message(
        chat_id,
        "🧪 **Тестовое уведомление**\n\n"
        "Это тестовое сообщение подтверждает, что ваша подписка активна "
        "и вы будете получать уведомления от SkillSwap!"
    )
    
    return {
        "status": "success" if success else "error",
        "message": "Тестовое уведомление отправлено" if success else "Не удалось отправить тестовое уведомление"
    }

@router.get("/admin/subscriptions", summary="Получить все подписки (админ)")
async def get_all_subscriptions(
    current_user = Depends(get_current_user)
):
    """Получение всех подписок (только для админов)"""
    # TODO: 
    subscriptions = await telegram_service.get_all_subscriptions()
    count = await telegram_service.get_subscriptions_count()
    
    return {
        "total_count": count,
        "subscriptions": subscriptions
    }

@router.get("/admin/stats", summary="Статистика подписок (админ)")
async def get_subscription_stats(
    current_user = Depends(get_current_user)
):
    """Статистика по подпискам (только для админов)"""
    # TODO: 
    count = await telegram_service.get_subscriptions_count()
    
    return {
        "total_subscriptions": count,
        "service_status": "active"
    }