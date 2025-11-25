# config.py
import os


class Config:
    # ----- DATABASE -----
    RAW_DB_URL = os.getenv("DATABASE_URL", "sqlite:///provent_dev.db")

    # תיקון ל־Render (postgres:// -> postgresql://)
    if RAW_DB_URL.startswith("postgres://"):
        RAW_DB_URL = RAW_DB_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = RAW_DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----- JWT -----
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Provent-Secret-Key-2025-CRM")

    # ----- CORS -----
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://crm.pro-net.pro")

    # ----- UPLOADS -----
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/mnt/uploads")
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB
