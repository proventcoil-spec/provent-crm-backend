# extensions.py
from flask_sqlalchemy import SQLAlchemy

# אובייקט ה-DB הגלובלי של האפליקציה
db = SQLAlchemy()


def init_db(app):
    """
    את הפונקציה הזו אתה קורא מתוך app.py
    היא מחברת את SQLAlchemy לאפליקציה
    ויוצרת את כל הטבלאות לפי המודלים.
    """
    db.init_app(app)

    # יוצרים את הטבלאות ב־PostgreSQL
    with app.app_context():
        # הייבוא כאן כדי למנוע import循环
        from models import User, Client, Lead, Event  # ודא שהקלאסים האלו קיימים ב-models.py
        db.create_all()
