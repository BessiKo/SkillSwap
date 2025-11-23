# app/database.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import Depends
import redis.asyncio as redis # Используем асинхронный клиент Redis
import os

from app.config import settings # Импортируем настройки

# --- SQLAlchemy / PostgreSQL ---
Base = declarative_base()

# URL для PostgreSQL
DATABASE_URL = settings.DATABASE_URL

# Синхронный URL для Alembic (без asyncpg)
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    """Dependency для получения асинхронной сессии БД."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# --- Redis ---
redis_client: redis.Redis | None = None

async def init_redis():
    """Инициализирует глобальное подключение к Redis."""
    global redis_client
    if settings.REDIS_URL:

        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

        await redis_client.ping() 
        print("Redis connection initialized successfully.")
    else:
        print("Warning: redis_url not set in settings. Redis features disabled.")

async def close_redis():
    """Закрывает глобальное подключение к Redis."""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("Redis connection closed.")

async def get_redis() -> redis.Redis:
    """Dependency для получения клиента Redis."""
    if redis_client is None:

        raise Exception("Redis client is not initialized. Check REDIS_URL in settings.")
    return redis_client