from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import jwt

from extensions import db
from models import User
from config import Config

auth_bp = Blueprint("auth", __name__)


def generate_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "שם משתמש או סיסמה לא נכונים"}), 401

    token = generate_token(user)

    return jsonify({
        "token": token,
        "user": user.to_dict()
    })


@auth_bp.route("/seed-admin", methods=["POST"])
def seed_admin():
    """יוצר משתמש אדמין פעם אחת"""
    existing = User.query.filter_by(email="admin@provent.co.il").first()
    if existing:
        return jsonify({"message": "Admin already exists"}), 200

    admin = User(
        username="admin",
        email="admin@provent.co.il",
        full_name="שלומי פרץ",
        role="owner",
        status="active",
    )

    admin.password_hash = generate_password_hash("Provent-2025!crm")

    db.session.add(admin)
    db.session.commit()

    return jsonify({"message": "Admin created"}), 201
