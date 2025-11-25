# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()


def init_db(app):
    # חיבור לדאטאבייס
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # יצירת טבלאות אם לא קיימות
    with app.app_context():
        db.create_all()

    # הגדרת CORS לכל ה־API
    CORS(
        app,
        resources={r"/api/*": {"origins": Config.FRONTEND_ORIGIN}},
        supports_credentials=True,
    )
