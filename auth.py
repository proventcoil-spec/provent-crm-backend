# auth.py
from flask import Blueprint, request, jsonify, current_app
from models import db, User
from passlib.hash import pbkdf2_sha256
import jwt
import datetime

auth_bp = Blueprint("auth_bp", __name__)


# הוספת CORS לכל הבקשות היוצאות מה־auth
@auth_bp.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ===== LOGIN =====
@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():

    # בקשת OPTIONS (Preflight)
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json() or {}

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"success": False, "error": "שם משתמש או סיסמה חסרים"}), 400

    # שליפת המשתמש מהמסד
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"success": False, "error": "שם המשתמש לא נמצא"}), 401

    # אימות סיסמה (hashed)
    if not pbkdf2_sha256.verify(password, user.password_hash):
        return jsonify({"success": False, "error": "סיסמה שגויה"}), 401

    # יצירת JWT
    secret = current_app.config.get("JWT_SECRET_KEY", "fallback_secret")
    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone
        }
    }), 200
