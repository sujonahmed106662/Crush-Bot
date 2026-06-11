import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile,
)

import database as db
from config import BOT_TOKEN, ADMIN_ID, BASE_URL

logger = logging.getLogger(__name__)

bot    = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp     = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


# ══════════════════════════════════════════════════════════════
#  KEYBOARDS
# ══════════════════════════════════════════════════════════════

def main_reply_kb(user_id: int = 0) -> ReplyKeyboardMarkup:
    """Persistent bottom keyboard — shown to every user after /start."""
    rows = [
        [KeyboardButton(text="💝 Crush Page বানাও"), KeyboardButton(text="📋 আমার Links")],
        [KeyboardButton(text="📊 আমার Stats"),        KeyboardButton(text="ℹ️ Help")],
    ]
    if user_id == ADMIN_ID:
        rows.append([KeyboardButton(text="🔧 Admin Panel"), KeyboardButton(text="📢 Broadcast")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, persistent=True)


def cancel_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ বাতিল করো")]],
        resize_keyboard=True,
    )


def links_selection_kb(links: list, prefix: str) -> ReplyKeyboardMarkup:
    """Build a reply keyboard listing user's pages by number for selection."""
    rows = []
    for i, link in enumerate(links, 1):
        rows.append([KeyboardButton(text=f"{i}. {link['crush_name']} ({link['link_id'][:6]}…)")])
    rows.append([KeyboardButton(text="❌ বাতিল করো")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# ══════════════════════════════════════════════════════════════
#  FSM STATES
# ══════════════════════════════════════════════════════════════

class CreateLink(StatesGroup):
    crush_name   = State()
    creator_name = State()
    message      = State()

class SelectLink(StatesGroup):
    """Generic state for selecting a link before customizing."""
    waiting = State()

class SetEmoji(StatesGroup):
    waiting = State()

class SetMusic(StatesGroup):
    waiting = State()

class SetBg(StatesGroup):
    waiting = State()

class SetMessage(StatesGroup):
    waiting = State()

class DeleteLink(StatesGroup):
    waiting = State()
    confirm = State()

class AdminBroadcast(StatesGroup):
    message = State()


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

async def check_banned(message: Message) -> bool:
    if db.is_banned(message.from_user.id):
        await message.answer("🚫 আপনাকে এই bot থেকে ban করা হয়েছে।")
        return True
    return False


def _find_link_from_selection(text: str, links: list) -> Optional[dict]:
    """Parse the user's reply keyboard selection and return matching link."""
    if not text:
        return None
    # Try matching "N. crush_name (id…)" pattern
    for i, link in enumerate(links, 1):
        expected = f"{i}. {link['crush_name']} ({link['link_id'][:6]}…)"
        if text.strip() == expected:
            return link
    # Fallback: try matching by number alone
    try:
        idx = int(text.split(".")[0].strip()) - 1
        if 0 <= idx < len(links):
            return links[idx]
    except (ValueError, IndexError):
        pass
    return None


def _verify_ownership(link: dict, user_id: int) -> bool:
    """Verify that the link belongs to the given user."""
    return link.get("user_id") == user_id


HELP_TEXT = (
    "📖 <b>Crush Proposal Bot — Help</b>\n\n"
    "<b>Button দিয়ে সহজে ব্যবহার করো:</b>\n"
    "💝 <b>Crush Page বানাও</b> — নতুন প্রপোজাল page তৈরি করো\n"
    "📋 <b>আমার Links</b> — তোমার সব page দেখো\n"
    "📊 <b>আমার Stats</b> — Views ও Yes সংখ্যা দেখো\n\n"
    "<b>Commands:</b>\n"
    "/create — নতুন crush page\n"
    "/mylinks — আমার links\n"
    "/stats — আমার stats\n"
    "/delete — page মুছে ফেলো\n"
    "/setemoji — floating emoji সেট করো\n"
    "/setbg — background image সেট করো\n"
    "/setmusic — background music সেট করো\n"
    "/setmessage — message আপডেট করো\n"
    "/cancel — যেকোনো কাজ বাতিল করো\n\n"
    "<b>কীভাবে কাজ করে:</b>\n"
    "1️⃣ Crush page বানাও ও link copy করো\n"
    "2️⃣ তোমার crush-কে link পাঠাও\n"
    "3️⃣ সে Yes ❤️ দিলে তুমি notification পাবে!\n\n"
    "💡 Unlimited page বানানো যাবে!"
)


# ══════════════════════════════════════════════════════════════
#  /start
# ══════════════════════════════════════════════════════════════

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    if await check_banned(message): return
    db.upsert_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    name = message.from_user.first_name or "বন্ধু"
    await message.answer(
        f"💕 <b>স্বাগতম, {name}!</b>\n\n"
        "Crush Proposal Bot-এ তোমাকে স্বাগত! 🌸\n\n"
        "তোমার crush-এর জন্য সুন্দর প্রপোজাল page বানাও এবং link শেয়ার করো।\n"
        "সে <b>Yes ❤️</b> দিলে তুমি Telegram-এ notification পাবে!\n\n"
        "নিচের button দিয়ে শুরু করো 👇",
        reply_markup=main_reply_kb(message.from_user.id),
    )


# ══════════════════════════════════════════════════════════════
#  HELP
# ══════════════════════════════════════════════════════════════

@router.message(Command("help"))
@router.message(F.text == "ℹ️ Help")
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_reply_kb(message.from_user.id))


# ══════════════════════════════════════════════════════════════
#  CREATE — Step 1: Crush name
# ══════════════════════════════════════════════════════════════

async def _start_create(message: Message, state: FSMContext):
    await state.clear()
    if await check_banned(message): return
    await state.set_state(CreateLink.crush_name)
    await message.answer(
        "💕 <b>Step 1 / 3</b>\n\nতোমার crush-এর নাম কী?",
        reply_markup=cancel_reply_kb(),
    )

@router.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
    await _start_create(message, state)

@router.message(F.text == "💝 Crush Page বানাও")
async def btn_create(message: Message, state: FSMContext):
    await _start_create(message, state)


@router.message(StateFilter(CreateLink.crush_name))
async def create_crush_name(message: Message, state: FSMContext):
    if await check_banned(message): return
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    if not text:
        await message.answer("⚠️ একটা নাম লেখো।"); return
    await state.update_data(crush_name=text)
    await state.set_state(CreateLink.creator_name)
    await message.answer(
        f"💌 Crush: <b>{text}</b>\n\n"
        "✏️ <b>Step 2 / 3</b>\n\nতোমার নিজের নাম কী?",
        reply_markup=cancel_reply_kb(),
    )


@router.message(StateFilter(CreateLink.creator_name))
async def create_creator_name(message: Message, state: FSMContext):
    if await check_banned(message): return
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    if not text:
        await message.answer("⚠️ একটা নাম লেখো।"); return
    await state.update_data(creator_name=text)
    await state.set_state(CreateLink.message)
    await message.answer(
        f"👤 তোমার নাম: <b>{text}</b>\n\n"
        "💬 <b>Step 3 / 3</b>\n\nতোমার crush-কে কী message পাঠাবে?\n"
        "<i>(Skip করতে /skip পাঠাও)</i>",
        reply_markup=cancel_reply_kb(),
    )


@router.message(StateFilter(CreateLink.message))
async def create_message_step(message: Message, state: FSMContext):
    if await check_banned(message): return
    data = await state.get_data()
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    if text.lower() == "/skip" or not text:
        custom_msg = f"💕 {data['creator_name']} তোমার জন্য special feeling রাখে!"
    else:
        custom_msg = text

    link_id  = db.create_link(
        user_id=message.from_user.id,
        crush_name=data["crush_name"],
        creator_name=data["creator_name"],
        message=custom_msg,
    )
    await state.clear()

    link_url = f"{BASE_URL}/p/{link_id}"
    await message.answer(
        f"🎉 <b>তোমার Crush Page তৈরি হয়ে গেছে!</b>\n\n"
        f"💕 Crush: <b>{data['crush_name']}</b>\n"
        f"👤 From: <b>{data['creator_name']}</b>\n\n"
        f"🔗 <b>এই link share করো:</b>\n{link_url}\n\n"
        f"<i>Page customize করো:</i>\n"
        f"🎭 /setemoji  🖼 /setbg  🎵 /setmusic\n\n"
        f"📋 Page ID: <code>{link_id}</code>",
        reply_markup=main_reply_kb(message.from_user.id),
    )


# ══════════════════════════════════════════════════════════════
#  MY LINKS
# ══════════════════════════════════════════════════════════════

async def _show_mylinks(message: Message):
    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer(
            "📋 তোমার কোনো crush page নেই।\n\n💝 প্রথমটা বানাও!",
            reply_markup=main_reply_kb(message.from_user.id),
        )
        return
    lines = ["📋 <b>তোমার Crush Pages:</b>\n"]
    for i, link in enumerate(links, 1):
        url = f"{BASE_URL}/p/{link['link_id']}"
        lines.append(
            f"{i}. 💕 <b>{link['crush_name']}</b>\n"
            f"   👁 Views: {link.get('views', 0)}  ❤️ Yes: {link.get('yes_count', 0)}\n"
            f"   🔗 {url}\n"
        )
    await message.answer("\n".join(lines), reply_markup=main_reply_kb(message.from_user.id))

@router.message(Command("mylinks"))
async def cmd_mylinks(message: Message):
    if await check_banned(message): return
    await _show_mylinks(message)

@router.message(F.text == "📋 আমার Links")
async def btn_mylinks(message: Message):
    if await check_banned(message): return
    await _show_mylinks(message)


# ══════════════════════════════════════════════════════════════
#  STATS
# ══════════════════════════════════════════════════════════════

def _stats_text(user_id: int) -> str:
    links = db.get_user_links(user_id)
    return (
        "📊 <b>তোমার Statistics</b>\n\n"
        f"📄 মোট pages:  <b>{len(links)}</b>\n"
        f"👁 মোট views:  <b>{sum(l.get('views', 0) for l in links)}</b>\n"
        f"❤️ মোট Yes:    <b>{sum(l.get('yes_count', 0) for l in links)}</b>\n"
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if await check_banned(message): return
    await message.answer(_stats_text(message.from_user.id), reply_markup=main_reply_kb(message.from_user.id))

@router.message(F.text == "📊 আমার Stats")
async def btn_stats(message: Message):
    if await check_banned(message): return
    await message.answer(_stats_text(message.from_user.id), reply_markup=main_reply_kb(message.from_user.id))


# ══════════════════════════════════════════════════════════════
#  SET EMOJI (Reply Keyboard selection)
# ══════════════════════════════════════════════════════════════

@router.message(Command("setemoji"))
async def cmd_setemoji(message: Message, state: FSMContext):
    if await check_banned(message): return
    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("⚠️ আগে /create দিয়ে page বানাও।", reply_markup=main_reply_kb(message.from_user.id)); return
    await state.update_data(action="setemoji", links_cache=[{"link_id": l["link_id"], "crush_name": l["crush_name"], "user_id": l["user_id"]} for l in links])
    await state.set_state(SelectLink.waiting)
    await message.answer(
        "🎭 কোন page-এর emoji বদলাবে?\nনিচে থেকে বেছে নাও 👇",
        reply_markup=links_selection_kb(links, "setemoji"),
    )

@router.message(Command("setmusic"))
async def cmd_setmusic(message: Message, state: FSMContext):
    if await check_banned(message): return
    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("⚠️ আগে /create দিয়ে page বানাও।", reply_markup=main_reply_kb(message.from_user.id)); return
    await state.update_data(action="setmusic", links_cache=[{"link_id": l["link_id"], "crush_name": l["crush_name"], "user_id": l["user_id"]} for l in links])
    await state.set_state(SelectLink.waiting)
    await message.answer(
        "🎵 কোন page-এ music দেবে?\nনিচে থেকে বেছে নাও 👇",
        reply_markup=links_selection_kb(links, "setmusic"),
    )

@router.message(Command("setbg"))
async def cmd_setbg(message: Message, state: FSMContext):
    if await check_banned(message): return
    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("⚠️ আগে /create দিয়ে page বানাও।", reply_markup=main_reply_kb(message.from_user.id)); return
    await state.update_data(action="setbg", links_cache=[{"link_id": l["link_id"], "crush_name": l["crush_name"], "user_id": l["user_id"]} for l in links])
    await state.set_state(SelectLink.waiting)
    await message.answer(
        "🖼 কোন page-এর background বদলাবে?\nনিচে থেকে বেছে নাও 👇",
        reply_markup=links_selection_kb(links, "setbg"),
    )

@router.message(Command("setmessage"))
async def cmd_setmessage(message: Message, state: FSMContext):
    if await check_banned(message): return
    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("⚠️ আগে /create দিয়ে page বানাও।", reply_markup=main_reply_kb(message.from_user.id)); return
    await state.update_data(action="setmessage", links_cache=[{"link_id": l["link_id"], "crush_name": l["crush_name"], "user_id": l["user_id"]} for l in links])
    await state.set_state(SelectLink.waiting)
    await message.answer(
        "💬 কোন page-এর message আপডেট করবে?\nনিচে থেকে বেছে নাও 👇",
        reply_markup=links_selection_kb(links, "setmessage"),
    )


# ── Generic link selection handler ────────────────────────────

@router.message(StateFilter(SelectLink.waiting))
async def select_link_handler(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return

    data = await state.get_data()
    links = data.get("links_cache", [])
    selected = _find_link_from_selection(text, links)

    if not selected:
        await message.answer("⚠️ সঠিক option বেছে নাও অথবা ❌ বাতিল করো।")
        return

    # Ownership validation
    if not _verify_ownership(selected, message.from_user.id):
        await state.clear()
        await message.answer("🚫 এটা তোমার page না!", reply_markup=main_reply_kb(message.from_user.id))
        return

    action = data.get("action", "")
    link_id = selected["link_id"]
    await state.update_data(link_id=link_id)

    if action == "setemoji":
        await state.set_state(SetEmoji.waiting)
        await message.answer("🎭 Emoji পাঠাও (যেমন: 💖 🌸 🦋 ✨):", reply_markup=cancel_reply_kb())
    elif action == "setmusic":
        await state.set_state(SetMusic.waiting)
        await message.answer("🎵 MP3 file-এর direct URL পাঠাও:", reply_markup=cancel_reply_kb())
    elif action == "setbg":
        await state.set_state(SetBg.waiting)
        await message.answer("🖼 Image-এর direct URL পাঠাও:", reply_markup=cancel_reply_kb())
    elif action == "setmessage":
        await state.set_state(SetMessage.waiting)
        await message.answer("💬 নতুন message লেখো:", reply_markup=cancel_reply_kb())
    else:
        await _cancel(message, state)


# ── Save handlers ─────────────────────────────────────────────

@router.message(StateFilter(SetEmoji.waiting))
async def setemoji_save(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    data = await state.get_data()
    db.update_link(data["link_id"], {"emoji": text or "❤️"})
    await state.clear()
    await message.answer(f"✅ Emoji আপডেট হয়েছে: {text}", reply_markup=main_reply_kb(message.from_user.id))


@router.message(StateFilter(SetMusic.waiting))
async def setmusic_save(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    data = await state.get_data()
    db.update_link(data["link_id"], {"music_url": text})
    await state.clear()
    await message.answer("✅ Background music আপডেট হয়েছে!", reply_markup=main_reply_kb(message.from_user.id))


@router.message(StateFilter(SetBg.waiting))
async def setbg_save(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    data = await state.get_data()
    db.update_link(data["link_id"], {"bg_image": text})
    await state.clear()
    await message.answer("✅ Background image আপডেট হয়েছে!", reply_markup=main_reply_kb(message.from_user.id))


@router.message(StateFilter(SetMessage.waiting))
async def setmsg_save(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    data = await state.get_data()
    db.update_link(data["link_id"], {"message": text})
    await state.clear()
    await message.answer("✅ Message আপডেট হয়েছে!", reply_markup=main_reply_kb(message.from_user.id))


# ══════════════════════════════════════════════════════════════
#  DELETE (Reply Keyboard)
# ══════════════════════════════════════════════════════════════

@router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext):
    if await check_banned(message): return
    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("⚠️ মুছার মতো কোনো page নেই।", reply_markup=main_reply_kb(message.from_user.id)); return
    await state.update_data(action="delete", links_cache=[{"link_id": l["link_id"], "crush_name": l["crush_name"], "user_id": l["user_id"]} for l in links])
    await state.set_state(DeleteLink.waiting)
    await message.answer(
        "🗑 কোন page মুছবে?\nনিচে থেকে বেছে নাও 👇",
        reply_markup=links_selection_kb(links, "delete"),
    )


@router.message(StateFilter(DeleteLink.waiting))
async def delete_select(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return

    data = await state.get_data()
    links = data.get("links_cache", [])
    selected = _find_link_from_selection(text, links)

    if not selected:
        await message.answer("⚠️ সঠিক option বেছে নাও অথবা ❌ বাতিল করো।")
        return

    # Ownership validation
    if not _verify_ownership(selected, message.from_user.id):
        await state.clear()
        await message.answer("🚫 এটা তোমার page না!", reply_markup=main_reply_kb(message.from_user.id))
        return

    await state.update_data(link_id=selected["link_id"], crush_name=selected["crush_name"])
    await state.set_state(DeleteLink.confirm)
    confirm_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ হ্যাঁ, মুছে ফেলো")],
            [KeyboardButton(text="❌ বাতিল করো")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        f"⚠️ <b>{selected['crush_name']}</b> page সত্যিই মুছে ফেলবে?",
        reply_markup=confirm_kb,
    )


@router.message(StateFilter(DeleteLink.confirm))
async def delete_confirm(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    if text == "✅ হ্যাঁ, মুছে ফেলো":
        data = await state.get_data()
        db.delete_link(data["link_id"])
        await state.clear()
        await message.answer(
            f"✅ <b>{data.get('crush_name', '')}</b> page মুছে ফেলা হয়েছে।",
            reply_markup=main_reply_kb(message.from_user.id),
        )
    else:
        await message.answer("⚠️ '✅ হ্যাঁ, মুছে ফেলো' বা '❌ বাতিল করো' বেছে নাও।")


# ══════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ══════════════════════════════════════════════════════════════

def admin_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 সব Users"), KeyboardButton(text="🔗 সব Links")],
            [KeyboardButton(text="📊 Admin Stats"), KeyboardButton(text="📢 Broadcast")],
            [KeyboardButton(text="🚫 User Ban"),   KeyboardButton(text="✅ User Unban")],
            [KeyboardButton(text="🏠 Main Menu")],
        ],
        resize_keyboard=True,
    )

async def _show_admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    stats = db.get_stats()
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\n"
        f"👥 Users:       <b>{stats['users']}</b>\n"
        f"🔗 Links:       <b>{stats['links']}</b>\n"
        f"👁 Views:       <b>{stats['views']}</b>\n"
        f"❤️ Yes clicks: <b>{stats['yes_clicks']}</b>\n\n"
        "নিচের button দিয়ে manage করো 👇",
        reply_markup=admin_reply_kb(),
    )

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await _show_admin_panel(message)

@router.message(F.text == "🔧 Admin Panel")
async def btn_admin(message: Message):
    await _show_admin_panel(message)


# ── Admin: Stats ──────────────────────────────────────────────

@router.message(F.text == "📊 Admin Stats")
async def btn_admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    stats = db.get_stats()
    await message.answer(
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users:      <b>{stats['users']}</b>\n"
        f"🔗 Total Links:      <b>{stats['links']}</b>\n"
        f"👁 Total Views:      <b>{stats['views']}</b>\n"
        f"❤️ Total Yes clicks: <b>{stats['yes_clicks']}</b>\n",
        reply_markup=admin_reply_kb(),
    )


# ── Admin: All Users ──────────────────────────────────────────

@router.message(F.text == "👥 সব Users")
async def btn_admin_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    users = db.get_all_users()
    if not users:
        await message.answer("কোনো user নেই।", reply_markup=admin_reply_kb()); return
    lines = [f"👥 <b>সব Users ({len(users)} জন):</b>\n"]
    for u in users[:30]:
        status = "🚫 Banned" if u.get("is_banned") else "✅"
        lines.append(f"{status} <code>{u['user_id']}</code> — @{u.get('username') or 'no_username'} ({u.get('full_name','')})")
    if len(users) > 30:
        lines.append(f"\n...এবং আরো {len(users)-30} জন")
    await message.answer("\n".join(lines), reply_markup=admin_reply_kb())


# ── Admin: All Links ──────────────────────────────────────────

@router.message(F.text == "🔗 সব Links")
async def btn_admin_links(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    links = [l for l in db.get_all_links() if not l.get("is_deleted")]
    if not links:
        await message.answer("কোনো link নেই।", reply_markup=admin_reply_kb()); return
    lines = [f"🔗 <b>সব Links ({len(links)} টি):</b>\n"]
    for l in links[:20]:
        lines.append(
            f"💕 <b>{l['crush_name']}</b> — "
            f"👁{l.get('views',0)} ❤️{l.get('yes_count',0)} — "
            f"<code>{l['link_id']}</code>"
        )
    if len(links) > 20:
        lines.append(f"\n...এবং আরো {len(links)-20} টি")
    await message.answer("\n".join(lines), reply_markup=admin_reply_kb())


# ── Admin: Ban ────────────────────────────────────────────────

@router.message(F.text == "🚫 User Ban")
async def btn_admin_ban_prompt(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    await message.answer(
        "🚫 Ban করতে লেখো:\n<code>/ban USER_ID</code>",
        reply_markup=admin_reply_kb(),
    )

@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Usage: /ban user_id"); return
    try:
        db.ban_user(int(parts[1]))
        await message.answer(f"✅ User <code>{parts[1]}</code> ban করা হয়েছে।", reply_markup=admin_reply_kb())
    except ValueError:
        await message.answer("⚠️ Invalid user ID.")


# ── Admin: Unban ──────────────────────────────────────────────

@router.message(F.text == "✅ User Unban")
async def btn_admin_unban_prompt(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    await message.answer(
        "✅ Unban করতে লেখো:\n<code>/unban USER_ID</code>",
        reply_markup=admin_reply_kb(),
    )

@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Usage: /unban user_id"); return
    try:
        db.unban_user(int(parts[1]))
        await message.answer(f"✅ User <code>{parts[1]}</code> unban করা হয়েছে।", reply_markup=admin_reply_kb())
    except ValueError:
        await message.answer("⚠️ Invalid user ID.")


# ── Admin: Broadcast ──────────────────────────────────────────

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    await state.set_state(AdminBroadcast.message)
    await message.answer("📢 Broadcast message লেখো:", reply_markup=cancel_reply_kb())

@router.message(F.text == "📢 Broadcast")
async def btn_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Admin only."); return
    await state.set_state(AdminBroadcast.message)
    await message.answer("📢 Broadcast message লেখো:", reply_markup=cancel_reply_kb())

@router.message(StateFilter(AdminBroadcast.message))
async def broadcast_send(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "❌ বাতিল করো":
        await _cancel(message, state); return
    await state.clear()
    users  = db.get_all_users()
    sent = failed = 0
    for user in users:
        if user.get("is_banned"): continue
        try:
            await bot.send_message(user["user_id"], f"📢 <b>Announcement</b>\n\n{text}")
            sent += 1
        except Exception:
            failed += 1
    await message.answer(
        f"📢 Broadcast শেষ!\n✅ Sent: {sent}  ❌ Failed: {failed}",
        reply_markup=admin_reply_kb(),
    )


# ── Admin: Main Menu back ─────────────────────────────────────

@router.message(F.text == "🏠 Main Menu")
async def btn_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Main Menu:", reply_markup=main_reply_kb(message.from_user.id))


# ══════════════════════════════════════════════════════════════
#  CANCEL
# ══════════════════════════════════════════════════════════════

async def _cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ বাতিল হয়েছে।", reply_markup=main_reply_kb(message.from_user.id))

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await _cancel(message, state)

@router.message(F.text == "❌ বাতিল করো")
async def btn_cancel(message: Message, state: FSMContext):
    await _cancel(message, state)


# ══════════════════════════════════════════════════════════════
#  NOTIFY CREATOR
# ══════════════════════════════════════════════════════════════

async def notify_creator(
    user_id: int,
    crush_name: str,
    date: str,
    time_str: str,
    image_path: Optional[str] = None,
):
    text = (
        "🎉 <b>SHE SAID YES! ❤️</b>\n\n"
        f"💕 Crush: <b>{crush_name}</b>\n"
        f"📅 Date:  <b>{date}</b>\n"
        f"⏰ Time:  <b>{time_str}</b>\n\n"
        "💌 তোমার প্রপোজাল accept হয়েছে! Congratulations! 🥰"
    )
    try:
        if image_path and os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await bot.send_photo(user_id, photo=photo, caption=text)
        else:
            await bot.send_message(user_id, text)
        db.save_notification(user_id, "", text)
    except Exception as e:
        logger.error(f"notify_creator failed for {user_id}: {e}")


async def start_polling():
    logger.info("Bot polling started…")
    await dp.start_polling(bot)
