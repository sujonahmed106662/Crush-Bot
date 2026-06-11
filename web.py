import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database as db
from image_generator import generate_yes_image
from config import BOT_TOKEN, BASE_URL, ADMIN_SECRET, WEBHOOK_MODE

logger = logging.getLogger(__name__)

BASE_DIR      = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR    = BASE_DIR / "static"
GENERATED_DIR = BASE_DIR / "generated"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    from firebase_config import get_db as _init_db
    try:
        _init_db()
        logger.info("Firebase initialised.")
    except Exception as e:
        logger.error(f"Firebase init failed: {e}")
        raise

    if not WEBHOOK_MODE and BOT_TOKEN:
        from bot import start_polling
        task = asyncio.create_task(start_polling())
        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    else:
        yield


app = FastAPI(title="Crush Proposal Bot", lifespan=lifespan)
app.mount("/static",    StaticFiles(directory=str(STATIC_DIR)),    name="static")
app.mount("/generated", StaticFiles(directory=str(GENERATED_DIR)), name="generated")


# ── Telegram webhook (production) ─────────────────────────────────────────────

@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    from bot import dp, bot as tg_bot
    from aiogram.types import Update
    data   = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(tg_bot, update)
    return {"ok": True}


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/p/{link_id}", response_class=HTMLResponse)
async def proposal_page(request: Request, link_id: str):
    link = db.get_link(link_id)
    if not link or link.get("is_deleted"):
        raise HTTPException(status_code=404, detail="Page not found")
    db.increment_views(link_id)
    return templates.TemplateResponse("proposal.html", {
        "request": request,
        "link":    link,
        "link_id": link_id,
    })


# ── Yes click ─────────────────────────────────────────────────────────────────

@app.post("/api/yes/{link_id}")
async def handle_yes(link_id: str):
    link = db.get_link(link_id)
    if not link or link.get("is_deleted"):
        raise HTTPException(status_code=404, detail="Link not found")

    result = db.record_yes(link_id, link["crush_name"], link["user_id"])

    image_path = None
    try:
        image_path = generate_yes_image(
            crush_name=link["crush_name"],
            creator_name=link["creator_name"],
            date=result["date"],
            time=result["time"],
            link_id=link_id,
        )
    except Exception as e:
        logger.error(f"Image generation failed: {e}")

    if BOT_TOKEN:
        try:
            from bot import notify_creator
            asyncio.create_task(notify_creator(
                user_id=link["user_id"],
                crush_name=link["crush_name"],
                date=result["date"],
                time_str=result["time"],
                image_path=image_path,
            ))
        except Exception as e:
            logger.error(f"Notification error: {e}")

    return JSONResponse({
        "status":       "ok",
        "crush_name":   link["crush_name"],
        "creator_name": link["creator_name"],
        "date":         result["date"],
        "time":         result["time"],
        "image_url":    f"/generated/{link_id}_yes.png" if image_path else None,
    })


# ── Admin ─────────────────────────────────────────────────────────────────────

def verify_admin(x_admin_secret: str = Header(default="")):
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {
        "request":      request,
        "admin_secret": ADMIN_SECRET,
    })

@app.get("/api/admin/stats")
async def admin_stats(_: bool = Depends(verify_admin)):
    return db.get_stats()

@app.get("/api/admin/users")
async def admin_users(_: bool = Depends(verify_admin)):
    users = db.get_all_users()
    for u in users:
        for k in list(u.keys()):
            if hasattr(u[k], "seconds"):
                u[k] = str(u[k])
    return users

@app.get("/api/admin/links")
async def admin_links(_: bool = Depends(verify_admin)):
    links = db.get_all_links()
    for l in links:
        for k in list(l.keys()):
            if hasattr(l[k], "seconds"):
                l[k] = str(l[k])
    return links

@app.post("/api/admin/ban/{user_id}")
async def admin_ban(user_id: int, _: bool = Depends(verify_admin)):
    db.ban_user(user_id)
    return {"status": "banned"}

@app.post("/api/admin/unban/{user_id}")
async def admin_unban(user_id: int, _: bool = Depends(verify_admin)):
    db.unban_user(user_id)
    return {"status": "unbanned"}

@app.delete("/api/admin/links/{link_id}")
async def admin_delete_link(link_id: str, _: bool = Depends(verify_admin)):
    db.delete_link(link_id)
    return {"status": "deleted"}

@app.post("/api/admin/broadcast")
async def admin_broadcast(request: Request, _: bool = Depends(verify_admin)):
    body = await request.json()
    msg  = body.get("message", "")
    if not msg:
        raise HTTPException(status_code=400, detail="Message required")
    users = db.get_all_users()
    sent = failed = 0
    if BOT_TOKEN:
        from bot import bot as tg_bot
        for user in users:
            if user.get("is_banned"):
                continue
            try:
                await tg_bot.send_message(user["user_id"], f"📢 {msg}")
                sent += 1
            except Exception:
                failed += 1
    return {"sent": sent, "failed": failed}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/healthz")
async def health():
    return {"status": "ok"}
