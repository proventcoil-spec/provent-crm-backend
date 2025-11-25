
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        "mysql+pymysql://{user}:{pw}@{host}/{db}?charset=utf8mb4".format(
            user=os.getenv("DB_USER", ""),
            pw=os.getenv("DB_PASS", ""),
            host=os.getenv("DB_HOST", "localhost"),
            db=os.getenv("DB_NAME", ""),
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Provent-Secret-Key-2025-CRM")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://crm.pro-net.pro")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/mnt/uploads")
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB
