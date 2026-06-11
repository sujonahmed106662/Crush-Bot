import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS

_db = None


def get_db():
    global _db
    if _db is None:
        _initialize_firebase()
    return _db


def _initialize_firebase():
    global _db
    if firebase_admin._apps:
        _db = firestore.client()
        return
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
