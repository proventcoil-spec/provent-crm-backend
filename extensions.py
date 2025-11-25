from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def init_db(app):
    # חיבור ל-PostgreSQL לפי DATABASE_URL של Render
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # יצירת טבלאות
    with app.app_context():
        db.create_all()
