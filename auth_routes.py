# auth_routes.py
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from extensions import db
from models import User
from config import Config

auth_bp = Blueprint("auth", __name__)

JWT_SECRET = Config.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"


# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "חסר אימייל או סיסמה"}), 400

    user = User.query.filter_by(email=email).first()

    # אם אין משתמש או שהסיסמה לא מתאימה
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "שם משתמש או סיסמה לא נכונים"}), 401

    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return jsonify(
        {
            "token": token,
            "user": user.to_dict(),
        }
    ), 200


# =========================
# SEED ADMIN  (פעם אחת בלבד)
# =========================
@auth_bp.route("/seed-admin", methods=["POST"])
def seed_admin():
    """
    יוצר משתמש אדמין ראשוני.
    עובד רק אם עדיין אין רשומת משתמש אחת ב-DB.
    אחרי שזה רץ פעם אחת – לא להשתמש בזה יותר.
    """

    # אם כבר יש משתמשים – חוסמים
    existing = User.query.first()
    if existing:
        return (
            jsonify({"message": "כבר קיימים משתמשים במערכת – יצירת אדמין חסומה"}),
            400,
        )

    # נתוני ברירת מחדל – אפשר לשנות פה אם תרצה
    email = "admin@provent.co.il"
    username = "admin"
    raw_password = "Provent-2025!"

    password_hash = generate_password_hash(raw_password)

    admin_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role="admin",
        full_name="Provent Admin",
        status="active",
    )

    db.session.add(admin_user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "אדמין נוצר בהצלחה",
                "login_email": email,
                "login_password": raw_password,
            }
        ),
        201,
    )
