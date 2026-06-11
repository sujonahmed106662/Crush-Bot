"""
Entry point — Railway production & local development.
All config is in config.py (env vars).
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


async def _register_webhook():
    """Register Telegram webhook (called inside existing event loop)."""
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    b = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    webhook_url = f"{BASE_URL.rstrip('/')}/webhook/{BOT_TOKEN}"
    await b.set_webhook(webhook_url, drop_pending_updates=True)
    info = await b.get_webhook_info()
    logger.info(f"Webhook registered → {info.url}")
    await b.session.close()


def setup_webhook():
    """Register Telegram webhook when WEBHOOK_MODE=True."""
    if not WEBHOOK_MODE:
        return
    if not BOT_TOKEN or not BASE_URL or "your-domain" in BASE_URL:
        logger.warning("Skipping webhook: BASE_URL not set or BOT_TOKEN missing")
        return

    # Use asyncio.run() only here at startup before uvicorn creates its loop
    try:
        loop = asyncio.get_running_loop()
        # If we're already inside a running loop, schedule as task
        loop.create_task(_register_webhook())
    except RuntimeError:
        # No running loop — safe to use asyncio.run()
        asyncio.run(_register_webhook())


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
