# bot/infra/webhook/handler.py

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from bot.core.config import config
from bot.infra.webhook.validator import validate_webhook_signature
import logging
import json

logger = logging.getLogger(__name__)

class WebhookHandler:
    """Обработчик вебхука Telegram"""
    
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
    
    async def handle_update(self, request: web.Request) -> web.Response:
        """Обработать входящее обновление от Telegram"""
        
        try:
            # Валидируем подпись (если включена)
            if config.WEBHOOK_SECRET:
                signature = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if not signature or signature != config.WEBHOOK_SECRET:
                    logger.warning("Invalid webhook signature")
                    return web.Response(status=401, text="Unauthorized")
            
            # Читаем тело запроса
            data = await request.json()
            
            # Логируем входящее событие
            logger.debug(f"Received update: {data.get('update_id')}")
            
            # Конвертируем в Update объект
            update = Update(**data)
            
            # Отправляем диспетчеру для обработки
            await self.dp.feed_update(self.bot, update)
            
            # Сразу возвращаем 200 OK (asynchronously обрабатываем дальше)
            return web.Response(status=200, text="OK")
        
        except Exception as e:
            logger.exception(f"Error handling webhook: {e}")
            return web.Response(status=500, text="Internal Server Error")
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Проверка здоровья (для балансировщика)"""
        return web.Response(status=200, text="OK")

async def setup_webhook_app() -> web.Application:
    """Создаём aiohttp приложение с вебхуком"""
    
    from bot.app.dispatcher import create_dispatcher
    
    app = web.Application()
    
    # Создаём бота и диспетчер
    bot = Bot(token=config.BOT_TOKEN)
    dp = await create_dispatcher()
    
    # Создаём обработчик
    handler = WebhookHandler(bot, dp)
    
    # Регистрируем маршруты
    app.router.post(config.WEBHOOK_PATH, handler.handle_update)
    app.router.get("/healthz", handler.health_check)
    
    return app
