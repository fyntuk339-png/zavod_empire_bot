# bot/domain/services/referral_service.py

from typing import Optional, Dict, Any
from bot.domain.models.referral import ReferralModel
from bot.domain.repositories.referral_repository import ReferralRepository
from bot.infra.cache.redis_client import redis_client
import secrets
import hashlib

class ReferralService:
    """Сервис управления реферальной системой"""
    
    def __init__(self, repository: ReferralRepository):
        self.repository = repository
    
    async def generate_referral_code(self, user_id: int) -> str:
        """Генерирует уникальный реф-код"""
        # Используем user_id + случайная часть
        random_part = secrets.token_hex(4)
        code = hashlib.md5(f"{user_id}{random_part}".encode()).hexdigest()[:16]
        return code.upper()
    
    async def get_referral_link(self, user_id: int) -> str:
        """Получить реф-ссылку пользователя"""
        # Проверяем кэш
        cached = await redis_client.get(f"referral_link:{user_id}")
        if cached:
            return cached.decode()
        
        # Получаем из БД
        referral = await self.repository.get_by_user_id(user_id)
        if not referral:
            code = await self.generate_referral_code(user_id)
            referral = await self.repository.create({
                'user_id': user_id,
                'referral_code': code,
                'bonus_amount': 50
            })
        
        link = f"https://t.me/zavod_empire_bot?start={referral['referral_code']}"
        
        # Кэшируем на 1 час
        await redis_client.setex(f"referral_link:{user_id}", 3600, link)
        
        return link
    
    async def process_referral_bonus(self, referral_code: str, new_user_id: int) -> int:
        """Обработать реф-бонус при присоединении нового пользователя"""
        # Получить реферера
        referrer = await self.repository.get_by_code(referral_code)
        if not referrer:
            return 0
        
        # Проверить лимиты (например, максимум 100 рефералов за день)
        daily_count = await self.repository.count_referrals_today(referrer['user_id'])
        if daily_count >= 100:
            return 0  # Лимит достигнут
        
        bonus = referrer['bonus_amount']
        
        # Отправить бонус реферу
        await self._credit_user(referrer['user_id'], bonus)
        
        # Отправить приветственный бонус новому пользователю
        welcome_bonus = int(bonus * 0.5)  # 50% от реф-бонуса
        await self._credit_user(new_user_id, welcome_bonus)
        
        return bonus
    
    async def _credit_user(self, user_id: int, amount: int) -> None:
        """Начислить валюту пользователю"""
        await self.repository.update_balance(user_id, amount)
        
        # Отправить уведомление
        # await telegram_notifications.send_bonus_notification(user_id, amount)
