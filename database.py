import uuid
import datetime
from typing import Optional

from firebase_admin import firestore as fb_firestore
from firebase_config import get_db

# Sentinel values — safe with firebase-admin 6.x
SERVER_TIMESTAMP = fb_firestore.SERVER_TIMESTAMP


def _increment(n=1):
    from google.cloud.firestore_v1 import transforms
    return transforms.Increment(n)


# ── Users ─────────────────────────────────────────────────────────────────────

def upsert_user(user_id: int, username: str = "", full_name: str = ""):
    db = get_db()
    ref = db.collection("users").document(str(user_id))
    doc = ref.get()
    if not doc.exists:
        ref.set({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "joined_at": SERVER_TIMESTAMP,
            "is_banned": False,
        })
    else:
        ref.update({"username": username, "full_name": full_name})


def get_user(user_id: int) -> Optional[dict]:
    db = get_db()
    doc = db.collection("users").document(str(user_id)).get()
    return doc.to_dict() if doc.exists else None


def is_banned(user_id: int) -> bool:
    user = get_user(user_id)
    return bool(user and user.get("is_banned"))


def ban_user(user_id: int):
    db = get_db()
    db.collection("users").document(str(user_id)).set(
        {"is_banned": True}, merge=True
    )
    db.collection("banned_users").document(str(user_id)).set(
        {"user_id": user_id, "banned_at": SERVER_TIMESTAMP}
    )


def unban_user(user_id: int):
    db = get_db()
    db.collection("users").document(str(user_id)).set(
        {"is_banned": False}, merge=True
    )
    db.collection("banned_users").document(str(user_id)).delete()


def get_all_users():
    db = get_db()
    return [d.to_dict() for d in db.collection("users").stream()]


# ── Links ──────────────────────────────────────────────────────────────────────

def create_link(
    user_id: int,
    crush_name: str,
    creator_name: str,
    message: str = "",
    bg_image: str = "",
    music_url: str = "",
    emoji: str = "❤️",
) -> str:
    db = get_db()
    link_id = uuid.uuid4().hex[:10]
    db.collection("links").document(link_id).set({
        "link_id": link_id,
        "user_id": user_id,
        "crush_name": crush_name,
        "creator_name": creator_name,
        "message": message,
        "bg_image": bg_image,
        "music_url": music_url,
        "emoji": emoji,
        "created_at": SERVER_TIMESTAMP,
        "views": 0,
        "yes_count": 0,
        "is_deleted": False,
    })
    return link_id


def get_link(link_id: str) -> Optional[dict]:
    db = get_db()
    doc = db.collection("links").document(link_id).get()
    return doc.to_dict() if doc.exists else None


def update_link(link_id: str, data: dict):
    db = get_db()
    db.collection("links").document(link_id).update(data)


def delete_link(link_id: str):
    db = get_db()
    db.collection("links").document(link_id).update({"is_deleted": True})


def get_user_links(user_id: int) -> list:
    """
    Query only by user_id (single-field index — no composite index needed).
    Filter is_deleted in Python to avoid Firestore composite index requirement.
    """
    db = get_db()
    docs = db.collection("links").where("user_id", "==", user_id).stream()
    return [d.to_dict() for d in docs if not d.to_dict().get("is_deleted")]


def get_all_links():
    db = get_db()
    return [d.to_dict() for d in db.collection("links").stream()]


def increment_views(link_id: str):
    db = get_db()
    db.collection("links").document(link_id).update({"views": _increment(1)})
    db.collection("views").add({
        "link_id": link_id,
        "timestamp": SERVER_TIMESTAMP,
    })


# ── Yes clicks ────────────────────────────────────────────────────────────────

def record_yes(link_id: str, crush_name: str, user_id: int) -> dict:
    db = get_db()
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S UTC")

    db.collection("yes_clicks").add({
        "link_id": link_id,
        "crush_name": crush_name,
        "user_id": user_id,
        "date": date_str,
        "time": time_str,
        "timestamp": SERVER_TIMESTAMP,
    })
    db.collection("links").document(link_id).update({"yes_count": _increment(1)})
    return {"date": date_str, "time": time_str}


# ── Stats ──────────────────────────────────────────────────────────────────────

def get_stats() -> dict:
    db = get_db()
    users_count = len(list(db.collection("users").stream()))
    all_links   = [d.to_dict() for d in db.collection("links").stream()]
    links_count = sum(1 for l in all_links if not l.get("is_deleted"))
    views_count = len(list(db.collection("views").stream()))
    yes_count   = len(list(db.collection("yes_clicks").stream()))
    return {
        "users":      users_count,
        "links":      links_count,
        "views":      views_count,
        "yes_clicks": yes_count,
    }


# ── Notifications ─────────────────────────────────────────────────────────────

def save_notification(user_id: int, link_id: str, message: str):
    db = get_db()
    db.collection("notifications").add({
        "user_id":  user_id,
        "link_id":  link_id,
        "message":  message,
        "sent_at":  SERVER_TIMESTAMP,
    })
