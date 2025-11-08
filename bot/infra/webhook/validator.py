# bot/infra/webhook/validator.py

import hmac
import hashlib
from bot.core.config import config

def validate_webhook_signature(
    body: bytes,
    telegram_signature: str
) -> bool:
    """Валидировать подпись webhook от Telegram"""
    
    secret_key = config.BOT_TOKEN.encode()
    expected_hash = hmac.new(
        secret_key,
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hash, telegram_signature)
