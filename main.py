"""
Entry point — Railway production & local development.
All config is in config.py (no env vars needed).
"""
import asyncio
import logging
import uvicorn
from config import BOT_TOKEN, BASE_URL, WEBHOOK_MODE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def setup_webhook():
    """Register Telegram webhook when WEBHOOK_MODE=True."""
    if not WEBHOOK_MODE:
        return
    if not BOT_TOKEN or not BASE_URL or "your-domain" in BASE_URL:
        logger.warning("Skipping webhook: BASE_URL not set in config.py")
        return

    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    async def _register():
        b = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        webhook_url = f"{BASE_URL.rstrip('/')}/webhook/{BOT_TOKEN}"
        await b.set_webhook(webhook_url, drop_pending_updates=True)
        info = await b.get_webhook_info()
        logger.info(f"Webhook registered → {info.url}")
        await b.session.close()

    asyncio.run(_register())


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))

    logger.info(f"PORT        : {port}")
    logger.info(f"BASE_URL    : {BASE_URL}")
    logger.info(f"WEBHOOK_MODE: {WEBHOOK_MODE}")

    setup_webhook()

    uvicorn.run(
        "web:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
    )
