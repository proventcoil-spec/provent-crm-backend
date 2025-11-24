# auth.py

from flask import Blueprint, request, jsonify, current_app
from models import db, User
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_
import jwt
import datetime

auth_bp = Blueprint("auth_bp", __name__)


# --------------------------------------------------
# CORS לכל הבקשות של auth
# --------------------------------------------------
@auth_bp.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# --------------------------------------------------
# LOGIN
# --------------------------------------------------
@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    # בקשת OPTIONS (Preflight)
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        data = request.get_json(silent=True) or {}

        # מהפרונט מגיע key בשם "username" אבל זה בעצם המייל בטופס
        identifier = (data.get("username") or data.get("email") or "").strip()
        password = (data.get("password") or "").strip()

        # אין מייל/יוזר או סיסמה
        if not identifier or not password:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        # חיפוש לפי username או לפי email
        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()

        if not user:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        # --------------------------------------------------
        # בדיקת סיסמה: hash או טקסט רגיל
        # --------------------------------------------------
        stored = getattr(user, "password_hash", None)
        if not stored:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        password_ok = False

        try:
            if isinstance(stored, str) and stored.startswith("$pbkdf2-sha256$"):
                # סיסמה מוצפנת
                password_ok = pbkdf2_sha256.verify(password, stored)
            else:
                # סיסמה רגילה בטבלה (כמו כרגע: Provent-2025)
                password_ok = (password == stored)
        except Exception:
            # אם יש בעיה ב-passlib, נעשה השוואה רגילה
            password_ok = (password == stored)

        if not password_ok:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        # --------------------------------------------------
        # יצירת JWT
        # --------------------------------------------------
        secret = current_app.config.get("JWT_SECRET_KEY", "fallback_jwt_secret")

        payload = {
            "sub": user.id,
            "username": user.username,
            "role": getattr(user, "role", None),
            "full_name": getattr(user, "full_name", None),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": getattr(user, "email", None),
            "full_name": getattr(user, "full_name", None),
            "role": getattr(user, "role", None),
        }

        return jsonify({
            "success": True,
            "message": "התחברת בהצלחה",
            "token": token,
            "user": user_data,
        }), 200

    except Exception as e:
        current_app.logger.exception("Error in /api/auth/login: %s", e)
        return jsonify({
            "success": False,
            "message": "שגיאה בשרת בזמן התחברות"
        }), 500
