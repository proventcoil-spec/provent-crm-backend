# auth_routes.py
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from extensions import db
from config import Config
from models import User  # חשוב: לוודא שהמודל User מוגדר ב-models.py

auth_bp = Blueprint("auth_bp", __name__)


# ---------- SEED ADMIN ----------

@auth_bp.route("/seed-admin", methods=["POST"])
def seed_admin():
    """
    יצירת משתמש אדמין ראשוני במערכת.
    אימייל:   admin@provent.co.il
    סיסמה:    Provent-2025
    """

    admin_email = "admin@provent.co.il"

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        return jsonify({"message": "Admin already exists"}), 200

    password_hash = generate_password_hash(
        "Provent-2025", method="pbkdf2:sha256", salt_length=8
    )

    admin = User(
        username="admin.master",
        email=admin_email,
        password_hash=password_hash,
        role="owner",
        full_name="שלומי פרץ",
        phone="0500000000",
        status="active",
        created_at=datetime.utcnow(),
    )

    db.session.add(admin)
    db.session.commit()

    return jsonify({"message": "Admin user created", "email": admin_email}), 201


# ---------- LOGIN ----------

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"message": "חסר אימייל או סיסמה"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "שם משתמש או סיסמה לא נכונים"}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"message": "שם משתמש או סיסמה לא נכונים"}), 401

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": getattr(user, "role", "user"),
        "exp": datetime.utcnow() + timedelta(days=1),
    }

    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

    return jsonify(
        {
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": getattr(user, "full_name", ""),
                "role": getattr(user, "role", "user"),
            },
        }
    ), 200
