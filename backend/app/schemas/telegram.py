from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TelegramSubscribe(BaseModel):
    chat_id: str

class TelegramStatus(BaseModel):
    is_subscribed: bool
    user_id: int

class BotInfo(BaseModel):
    bot_username: str
    bot_url: str
    instructions: str
    enabled: bool

class SubscriptionInfo(BaseModel):
    user_id: int
    chat_id: str
    subscribed_at: str

class SubscriptionsResponse(BaseModel):
    total_count: int
    subscriptions: list[SubscriptionInfo]

class StatsResponse(BaseModel):
    total_subscriptions: int
    service_status: str