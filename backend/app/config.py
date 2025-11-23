from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Класс настроек приложения, загружаемых из переменных окружения
    или файла .env.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"   
    )

 
    APP_NAME: str = "SkillSwap API"

    DEBUG: bool = False 

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/skillswap"

    REDIS_URL: str = "redis://localhost:6379/0" 

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMS_PROVIDER: str = "mock" 

    SMS_API_KEY: Optional[str] = None

    CODE_EXPIRY: int = 300 

    CODE_REQUEST_LIMIT: int = 5 

    CODE_REQUEST_WINDOW: int = 3600

    TELEGRAM_BOT_TOKEN: Optional[str] = None

    TELEGRAM_BOT_USERNAME: Optional[str] = "SkillSwapNotifierBot"
    

    MAX_FILE_SIZE: int = 10 * 1024 * 1024 
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:5173",
    ]

settings = Settings()

def get_telegram_bot_url() -> Optional[str]:
    """Генерирует URL для телеграм бота"""
    if settings.TELEGRAM_BOT_USERNAME:
        return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}"
    return None

def is_telegram_enabled() -> bool:
    """Проверяет, включены ли телеграм уведомления"""
    return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_USERNAME)

