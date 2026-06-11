# ════════════════════════════════════════════════════════
#  ALL CONFIGURATION — uses environment variables with fallbacks
# ════════════════════════════════════════════════════════
import os
import json

BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")
ADMIN_ID     = int(os.environ.get("ADMIN_ID", "0"))
BASE_URL     = os.environ.get("BASE_URL", "https://your-domain.up.railway.app")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "crush_admin_2024")
WEBHOOK_MODE = os.environ.get("WEBHOOK_MODE", "false").lower() in ("true", "1", "yes")

# Firebase service account — from FIREBASE_CREDENTIALS_JSON env var (JSON string)
# Or fallback to individual env vars
_firebase_json = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")

if _firebase_json:
    FIREBASE_CREDENTIALS = json.loads(_firebase_json)
else:
    # Build from individual env vars (for Railway / Render convenience)
    _private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    FIREBASE_CREDENTIALS = {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID", ""),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": _private_key,
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL", ""),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get("FIREBASE_CERT_URL", ""),
        "universe_domain": "googleapis.com",
    }
