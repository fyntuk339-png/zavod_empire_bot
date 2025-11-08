# bot/app/middlewares/i18n.py

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, types
from aiogram.types import Message
from bot.infra.cache.redis_client import redis_client
import gettext
import os

class I18nMiddleware(BaseMiddleware):
    """Middleware для многоязычности (i18n)"""
    
    def __init__(self, default_locale: str = "ru", locales_dir: str = "bot/locales"):
        self.default_locale = default_locale
        self.locales_dir = locales_dir
        self.translations = {}
        self._load_translations()
        super().__init__()
    
    def _load_translations(self):
        """Загружаем все переводы"""
        for lang in os.listdir(self.locales_dir):
            lang_path = os.path.join(self.locales_dir, lang, "LC_MESSAGES", "messages.mo")
            if os.path.exists(lang_path):
                self.translations[lang] = gettext.GNUTranslations(open(lang_path, "rb"))
    
    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: Dict[str, Any]
    ) -> Any:
        """Установить язык в контекст"""
        
        message = event.message or event.callback_query.message
        user_id = message.from_user.id
        
        # Получить язык из кэша
        cached_lang = await redis_client.get(f"user_lang:{user_id}")
        if cached_lang:
            language = cached_lang.decode()
        else:
            # Использовать язык Telegram пользователя или по умолчанию
            language = message.from_user.language_code or self.default_locale
            await redis_client.setex(f"user_lang:{user_id}", 86400, language)
        
        # Установить переводчик в данные
        translator = self.translations.get(language, self.translations.get(self.default_locale))
        data["locale"] = language
        data["i18n"] = translator
        
        return await handler(event, data)
