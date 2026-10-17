import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "mannmitra-mindful-secret-key-2026")
    MONGO_URI = os.getenv("MONGO_URI", "")
    DB_NAME = os.getenv("DB_NAME", "mannmitra")
    PERMANENT_SESSION_LIFETIME = timedelta(days=60)
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False

