# bot/core/config.py

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
import logging

class BotConfig(BaseSettings):
    """Конфигурация бота"""
    
    # Bot
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token")
    WEBHOOK_HOST: str = Field(..., description="Webhook хост (например, https://api.example.com)")
    WEBHOOK_PORT: int = Field(443, description="HTTPS порт")
    WEBHOOK_PATH: str = Field("/webhook", description="Путь webhook")
    WEBHOOK_SECRET: Optional[str] = Field(None, description="Секрет для валидации")
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL DSN")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = Field(..., description="Redis DSN")
    REDIS_DB: int = 0
    
    # RQ
    RQ_REDIS_URL: Optional[str] = None
    RQ_JOB_TIMEOUT: int = 300
    RQ_RESULT_TTL: int = 500
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Admin
    ADMIN_IDS: list[int] = Field(default_factory=list)
    
    # Features
    ENABLE_REFERRALS: bool = True
    ENABLE_AUCTIONS: bool = True
    ENABLE_FACTORY_UPGRADES: bool = True
    
    # I18n
    DEFAULT_LANGUAGE: str = "ru"
    SUPPORTED_LANGUAGES: list[str] = ["ru", "en"]
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW: int = 1  # секунды
    
    class Config:
        env_file = ".env"
        case_sensitive = True

config = BotConfig()
