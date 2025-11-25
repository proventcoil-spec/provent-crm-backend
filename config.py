import os

class Config:
    # חיבור ל-DB: אם יש DATABASE_URL – משתמשים בו, אחרת sqlite מקומי
    RAW_DB_URL = os.getenv("DATABASE_URL", "sqlite:///provent_dev.db")

    SQLALCHEMY_DATABASE_URI = RAW_DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # נשאיר מפתח JWT לעתיד אם תרצה להוסיף טוקנים
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Provent-Secret-Key-2025-CRM")

    # מאיפה מותר לגשת ל-API
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://crm.pro-net.pro")

    # תקיית העלאות – לעתיד
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/mnt/uploads")
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB
