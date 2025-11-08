"""
ZAVOD EMPIRE BOT - Main entry point
"""
import asyncio
import logging
from bot.core.config import config
from bot.infra.webhook.handler import setup_webhook_app
from aiohttp import web

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

async def main():
    """Main application entry point"""
    app = await setup_webhook_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.WEBHOOK_PORT)
    await site.start()
    
    logger.info(f"🤖 Bot started on {config.WEBHOOK_HOST}{config.WEBHOOK_PATH}")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
