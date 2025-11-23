from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

print(f"🔧 DEBUG: Current directory: {os.getcwd()}")
print(f"🔧 DEBUG: TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN')}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, init_redis, close_redis
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.ads import router as ads_router
from app.api.chat import router as chat_router
from app.api.deal import router as deal_router
from app.api.admin import router as admin_router


try:
    from app.api.gamification import router as gamification_router
    GAMIFICATION_ENABLED = True
    print("✅ Gamification router imported successfully")
except ImportError as e:
    print(f"⚠️  Gamification router not available: {e}")
    GAMIFICATION_ENABLED = False

    from fastapi import APIRouter
    gamification_router = APIRouter(prefix="/gamification", tags=["Gamification"])

try:
    from app.api.telegram import router as telegram_router
    TELEGRAM_ENABLED = True
    print("✅ Telegram router imported successfully")
except ImportError as e:
    print(f"⚠️  Telegram router not available: {e}")
    TELEGRAM_ENABLED = False

    from fastapi import APIRouter
    telegram_router = APIRouter(prefix="/telegram", tags=["Telegram"])

try:
    from app.telegram.bot import telegram_bot_instance
    TELEGRAM_BOT_ENABLED = True
    print("✅ Telegram bot imported successfully")
except ImportError as e:
    print(f"⚠️  Telegram bot not available: {e}")
    TELEGRAM_BOT_ENABLED = False
    telegram_bot_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan менеджер для управления событиями запуска и остановки приложения.
    """

    print("🚀 Starting SkillSwap API...")
    
    create_required_directories()
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

    try:
        await init_redis()
        print("✅ Redis connection initialized")
    except Exception as e:
        print(f"❌ Redis initialization error: {e}")
        raise

    if TELEGRAM_BOT_ENABLED and telegram_bot_instance:
        try:
            await telegram_bot_instance.start()
            print("✅ Telegram bot started successfully")
        except Exception as e:
            print(f"⚠️  Telegram bot startup error: {e}")
    else:
        print(f"⏭️  Telegram bot disabled - TELEGRAM_BOT_ENABLED: {TELEGRAM_BOT_ENABLED}, instance: {bool(telegram_bot_instance)}")
    

    try:
        await seed_initial_data()
        print("✅ Initial data seeded successfully")
    except Exception as e:
        print(f"⚠️  Initial data seeding error: {e}")
    
    yield

    print("🛑 Shutting down SkillSwap API...")
    
    if TELEGRAM_BOT_ENABLED and telegram_bot_instance:
        try:
            await telegram_bot_instance.stop()
            print("✅ Telegram bot stopped successfully")
        except Exception as e:
            print(f"⚠️  Telegram bot shutdown error: {e}")

    await close_redis()
    await engine.dispose()
    print("✅ Connections closed successfully")

def create_required_directories():
    """Создание всех необходимых директорий."""
    directories = [
        "uploads/avatars",
        "uploads/ads",
        "logs",
        "static"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory created: {directory}")

async def seed_initial_data():
    """
    Заполнение базы данных начальными данными.
    """
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.user import Badge, BadgeType
    
    async with AsyncSessionLocal() as db:

        try:
            result = await db.execute(select(Badge))
            if not result.scalars().first():
                badges = [
                    Badge(name="Новичок", type=BadgeType.NEWCOMER, description="Добро пожаловать в Скилл Свап!", icon="👋"),
                    Badge(name="Первый обмен", type=BadgeType.FIRST_EXCHANGE, description="Провёл первый обмен знаниями", icon="🎯"),
                    Badge(name="Популярный", type=BadgeType.POPULAR, description="10+ успешных обменов", icon="⭐"),
                    Badge(name="Топ рейтинг", type=BadgeType.TOP_RATED, description="Рейтинг 4.8+ с 5+ отзывами", icon="🏆"),
                    Badge(name="Ментор", type=BadgeType.MENTOR, description="25+ успешных обменов", icon="🎓"),
                    Badge(name="Эксперт", type=BadgeType.EXPERT, description="50+ успешных обменов", icon="💎"),
                ]
                db.add_all(badges)
                await db.commit()
                print("✅ Basic badges seeded")
        except Exception as e:
            print(f"⚠️  Basic badges seeding error: {e}")
            await db.rollback()

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    🎓 SkillSwap API - P2P платформа для обмена знаниями внутри университета.
    
    ## Возможности
    
    * 🔐 **Аутентификация по SMS** - безопасный вход по номеру телефона
    * 📚 **Объявления** - создание и поиск предложений по обмену знаниями
    * 💬 **Чаты** - общение между пользователями
    * 🤝 **Сделки** - управление процессом обмена знаний
    * 🏆 **Геймификация** - система уровней, значков и рейтингов
    * 👨‍💼 **Админ-панель** - управление пользователями и контентом
    * 🤖 **Telegram уведомления** - получение уведомлений в Telegram
    * 🔄 **WebSocket** - реальное время для чатов и уведомлений
    """,
    version="2.1.0",
    contact={
        "name": "SkillSwap Support",
        "url": "https://github.com/skillswap/support",
        "email": "support@skillswap.com",
    },
    license_info={
        "name": "license",
        "url": "https://i.pinimg.com/736x/3a/d5/ec/3ad5ecc637826ce1960a7c89154aef93.jpg",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "🔐 Аутентификация по SMS",
        },
        {
            "name": "Users", 
            "description": "👥 Управление пользователями",
        },
        {
            "name": "Ads",
            "description": "📚 Объявления и поиск",
        },
        {
            "name": "Chats",
            "description": "💬 Чаты и сообщения", 
        },
        {
            "name": "Deals",
            "description": "🤝 Сделки и обмены",
        },
        {
            "name": "Admin",
            "description": "👨‍💼 Администрирование",
        },
        {
            "name": "Gamification",
            "description": "🏆 Система геймификации",
        },
        {
            "name": "Telegram",
            "description": "🤖 Telegram уведомления",
        }
    ]
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")


api_routers = [
    auth_router,           # 🔐 Аутентификация
    users_router,          # 👥 Пользователи
    ads_router,            # 📚 Объявления
    chat_router,           # 💬 Чаты
    deal_router,           # 🤝 Сделки
    admin_router,          # 👨‍💼 Админ-панель
    gamification_router,   # 🏆 Геймификация (всегда включаем)
    telegram_router,       # 🤖 Telegram уведомления
]

for router in api_routers:
    app.include_router(router, prefix="/api/v1")
    print(f"✅ Router included: {router.prefix}")

@app.get("/")
async def root():
    """
    Корневой endpoint для проверки работы API.
    """
    return {
        "message": "🎓 SkillSwap API is running!",
        "version": "2.1.0",
        "status": "healthy",
        "docs": "/docs",
        "features": [
            "SMS Authentication",
            "Knowledge Exchange Platform", 
            "Real-time Chat",
            "Gamification System",
            "Telegram Notifications",
            "Admin Panel"
        ]
    }

@app.get("/health")
async def health_check():
    """
    Endpoint для проверки здоровья приложения.
    """
    from app.database import get_redis
    from redis.exceptions import RedisError
    from datetime import datetime

    db_status = "healthy"
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        db_status = "unhealthy"

    redis_status = "healthy"
    try:
        redis_client = await get_redis()
        await redis_client.ping()
    except (RedisError, Exception):
        redis_status = "unhealthy"
    
    telegram_status = "healthy"
    if TELEGRAM_BOT_ENABLED and telegram_bot_instance:
        try:
            if telegram_bot_instance.is_running:
                telegram_status = "healthy"
            else:
                telegram_status = "disabled"
        except Exception:
            telegram_status = "unhealthy"
    else:
        telegram_status = "disabled"
    
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": db_status,
            "redis": redis_status,
            "telegram_bot": telegram_status,
            "api": "healthy"
        },
        "version": "2.1.0"
    }

@app.get("/info")
async def api_info():
    """
    Информация о API и доступных эндпоинтах.
    """
    return {
        "api_name": settings.APP_NAME,
        "version": "2.1.0",
        "environment": "development" if settings.DEBUG else "production",
        "debug_mode": settings.DEBUG,
        "endpoints": {
            "authentication": "/api/v1/auth",
            "users": "/api/v1/users",
            "ads": "/api/v1/ads",
            "chats": "/api/v1/chats",
            "deals": "/api/v1/deals",
            "admin": "/api/v1/admin",
            "gamification": "/api/v1/gamification",
            "telegram": "/api/v1/telegram"
        },
        "features": {
            "sms_verification": True,
            "real_time_chat": True,
            "gamification": GAMIFICATION_ENABLED,
            "telegram_notifications": TELEGRAM_ENABLED,
            "admin_panel": True,
            "file_uploads": True
        }
    }


@app.get("/test-telegram")
async def test_telegram():
    """Тестовый endpoint для проверки Telegram бота"""
    if not TELEGRAM_BOT_ENABLED:
        return {"error": "Telegram bot disabled"}
    
    return {
        "bot_running": telegram_bot_instance.is_running,
        "has_token": bool(telegram_bot_instance.token),
        "status": "active" if telegram_bot_instance.is_running else "inactive"
    }


@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware для логирования входящих запросов.
    """
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"📨 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
    
    return response

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )