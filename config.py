import os

class Config:
    RAW_DB_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")

    # תיקון כתובת render:
    if RAW_DB_URL.startswith("postgres://"):
        RAW_DB_URL = RAW_DB_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = RAW_DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Provent-Secret-2025")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://crm.pro-net.pro")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/mnt/uploads")
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB
