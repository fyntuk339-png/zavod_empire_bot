# bot/app/middlewares/rate_limit.py

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, types
from aiogram.types import Message
from bot.infra.cache.redis_client import redis_client
import time
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseMiddleware):
    """Middleware для rate limiting (Token Bucket)"""
    
    def __init__(self, rate: int = 30, window: int = 1):
        """
        rate: количество запросов
        window: временное окно в секундах
        """
        self.rate = rate
        self.window = window
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: Dict[str, Any]
    ) -> Any:
        """Проверить rate limit перед обработкой"""
        
        message = event.message
        if not message:
            return await handler(event, data)
        
        user_id = message.from_user.id
        key = f"rate_limit:{user_id}"
        
        # Получить текущее количество токенов
        current = await redis_client.get(key)
        if current is None:
            # Первый запрос - устанавливаем максимум токенов
            await redis_client.setex(key, self.window, self.rate - 1)
            return await handler(event, data)
        
        tokens = int(current)
        if tokens <= 0:
            # Лимит превышен
            logger.warning(f"Rate limit exceeded for user {user_id}")
            await message.answer("⏱️ Вы отправляете сообщения слишком быстро. Попробуйте позже.")
            return
        
        # Уменьшаем количество токенов
        await redis_client.decr(key)
        
        return await handler(event, data)
