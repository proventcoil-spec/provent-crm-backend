import os
from urllib.parse import quote_plus

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # אם יש DATABASE_URL (ברנדר), נשתמש בו. אחרת SQLite מקומי
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "provent_crm.db")

    # הגדרות 019 SMS (להחליף בפרטים אמיתיים)
    SMS_019_USERNAME = os.environ.get("SMS_019_USERNAME", "")
    SMS_019_PASSWORD = os.environ.get("SMS_019_PASSWORD", "")
    SMS_019_API_KEY = os.environ.get("SMS_019_API_KEY", "")
    SMS_019_SENDER = os.environ.get("SMS_019_SENDER", "PROVENT")

def get_config():
    return Config
