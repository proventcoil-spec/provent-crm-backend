from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt

db = SQLAlchemy()


def init_db(app):
    """
    מחבר את SQLAlchemy לאפליקציה ויוצר טבלאות.
    בנוסף – יוצר משתמש אדמין אם עוד לא קיים.
    """
    db.init_app(app)

    from models import User  # ייבוא דינמי כדי לא לעשות לולאת import

    with app.app_context():
        db.create_all()

        # יצירת משתמש אדמין ברירת מחדל אם אין כזה
        admin_email = "admin@provent.co.il"
        admin_password = "Provent-2025!crm"

        existing = User.query.filter_by(email=admin_email).first()
        if not existing:
            admin = User(
                email=admin_email,
                full_name="שלומי פרץ",
                role="owner",
                status="active",
            )
            admin.password_hash = bcrypt.hash(admin_password)
            db.session.add(admin)
            db.session.commit()
