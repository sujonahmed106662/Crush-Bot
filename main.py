"""
Entry point — Railway production & local development.
All config is in config.py (hardcoded — কিছু সেট করতে হবে না).
"""
import asyncio
import logging
import os
import uvicorn
from config import BOT_TOKEN, WEBHOOK_MODE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_base_url() -> str:
    """Auto-detect Railway public URL at runtime."""
    import config
    # Railway provides RAILWAY_PUBLIC_DOMAIN automatically
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
    if domain:
        url = f"https://{domain}"
        config.BASE_URL = url
        return url
    return config.BASE_URL


async def _register_webhook(base_url: str):
    """Register Telegram webhook."""
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    b = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    webhook_url = f"{base_url.rstrip('/')}/webhook/{BOT_TOKEN}"
    await b.set_webhook(webhook_url, drop_pending_updates=True)
    info = await b.get_webhook_info()
    logger.info(f"Webhook registered → {info.url}")
    await b.session.close()


def setup_webhook(base_url: str):
    """Register Telegram webhook when WEBHOOK_MODE=True."""
    if not WEBHOOK_MODE:
        return
    if not BOT_TOKEN or not base_url or "your-domain" in base_url:
        logger.warning("Skipping webhook: BASE_URL not available yet (will register on first request)")
        return

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_register_webhook(base_url))
    except RuntimeError:
        asyncio.run(_register_webhook(base_url))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    base_url = get_base_url()

    logger.info(f"PORT        : {port}")
    logger.info(f"BASE_URL    : {base_url}")
    logger.info(f"WEBHOOK_MODE: {WEBHOOK_MODE}")

    setup_webhook(base_url)

    uvicorn.run(
        "web:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
    )
