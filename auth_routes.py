# auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from models import db, User
from passlib.hash import pbkdf2_sha256
import jwt
import datetime
from sqlalchemy import or_

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.after_request
def add_cors_headers(response):
    """
    להוסיף CORS לכל תגובה שיוצאת מה-auth
    """
    # אם הגדרת ALLOWED_ORIGINS ב-config – נשתמש בו, אחרת נאפשר לכולם
    allowed_origins = current_app.config.get("ALLOWED_ORIGINS", "*")
    response.headers["Access-Control-Allow-Origin"] = allowed_origins
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    # לטפל ב-Preflight של הדפדפן
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json() or {}

    # אפשר לזהות גם לפי email וגם לפי username – מה שהפרונט שולח
    identifier = (data.get("email") or data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not identifier or not password:
        return jsonify({
            "success": False,
            "error": "שם משתמש או סיסמה לא נכונים"
        }), 401

    # למצוא לפי אימייל או יוזרניימ
    user = User.query.filter(
        or_(User.email == identifier, User.username == identifier)
    ).first()

    if not user:
        return jsonify({
            "success": False,
            "error": "שם משתמש או סיסמה לא נכונים"
        }), 401

    # בדיקת סיסמה מול ה-hash
    if not pbkdf2_sha256.verify(password, user.password_hash):
        return jsonify({
            "success": False,
            "error": "שם משתמש או סיסמה לא נכונים"
        }), 401

    # יצירת JWT
    secret = current_app.config.get("JWT_SECRET_KEY", "Provent-JWT-Secret-2025")
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
        "iat": datetime.datetime.utcnow(),
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }
    }), 200
