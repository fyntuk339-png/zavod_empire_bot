# bot/infra/cache/rate_limiter.py

from bot.infra.cache.redis_client import redis_client
import time

class RedisTokenBucket:
    """Token Bucket rate limiter с Redis"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity: максимум токенов в bucket
        refill_rate: токены/сек
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
    
    async def is_allowed(self, key: str) -> bool:
        """Проверить, разрешён ли запрос"""
        
        now = time.time()
        data = await redis_client.get(f"rate_limit:{key}")
        
        if not data:
            # Первый запрос
            await redis_client.set(
                f"rate_limit:{key}",
                f"{self.capacity - 1},{now}",
                ex=int(self.capacity / self.refill_rate) + 1
            )
            return True
        
        # Парсим данные
        tokens_str, last_refill_str = data.decode().split(',')
        tokens = int(tokens_str)
        last_refill = float(last_refill_str)
        
        # Рефиллим токены
        elapsed = now - last_refill
        refilled = int(elapsed * self.refill_rate)
        tokens = min(self.capacity, tokens + refilled)
        
        if tokens > 0:
            # Даём токен
            tokens -= 1
            await redis_client.set(
                f"rate_limit:{key}",
                f"{tokens},{now}",
                ex=int(self.capacity / self.refill_rate) + 1
            )
            return True
        
        return False
