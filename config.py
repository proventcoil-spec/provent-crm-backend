# config.py

import os

class Config:
    # ---- חיבור למסד הנתונים (MySQL ב-Hostinger) ----
    # Render יקרא את ה-DATABASE_URL מה־Environment,
    # ואם לא הגדרת – הוא יפול לברירת המחדל פה (לא מומלץ בפרודקשן).
    DB_USER = os.getenv("DB_USER", "u894002499_provicrm")
    DB_PASS = os.getenv("DB_PASS", "CHANGE_ME_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "mysqlXXX.hostinger.com")
    DB_NAME = os.getenv("DB_NAME", "u894002499_provicrm")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- מפתחות סודיים ----
    SECRET_KEY = os.getenv("SECRET_KEY", "provent-secret-key-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "provent-jwt-secret-key-change-me")

    # ---- CORS ----
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://crm.pro-net.pro,http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")

    # ---- 019 SMS ----
    SMS019_USERNAME = os.getenv("SMS019_USERNAME", "provent12")
    SMS019_PASSWORD = os.getenv("SMS019_PASSWORD", "Provent-2025")
    SMS019_SOURCE   = os.getenv("SMS019_SOURCE", "provent")  # שם השולח בטקסטואל


def get_config():
    return Config
