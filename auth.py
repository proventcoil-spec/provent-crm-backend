# auth.py

from flask import Blueprint, request, jsonify, current_app
from models import db, User
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
import jwt
import datetime

auth_bp = Blueprint("auth_bp", __name__)


# --------------------------------------------------
# CORS לכל הבקשות שיוצאות דרך auth
# --------------------------------------------------
@auth_bp.after_request
def add_cors_headers(response):
    # אם הגדרת ALLOWED_ORIGINS ב-app.config – נשתמש בו, אחרת נפתח ל-*
    allowed_origins = current_app.config.get("ALLOWED_ORIGINS", "*")
    response.headers["Access-Control-Allow-Origin"] = allowed_origins
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# --------------------------------------------------
# LOGIN
# --------------------------------------------------
@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    # בקשת OPTIONS (Preflight) לדפדפן – נחזיר OK
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        data = request.get_json(silent=True) or {}

        # בשורה הזו מגיע מהפרונט השדה username – אבל זה בעצם אימייל אצלך
        username_or_email = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username_or_email or not password:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 400

        # נחפש גם לפי username וגם לפי email
        user = (
            User.query
            .filter(
                or_(User.username == username_or_email,
                    User.email == username_or_email)
            )
            .first()
        )

        if not user:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        # --------------------------------------------------
        # בדיקת סיסמה:
        # אם השדה נראה כמו hash של pbkdf2 – נשתמש ב-verify
        # אחרת נשווה טקסט רגיל (כמו שיש כרגע ב-DB: Provent-2025)
        # --------------------------------------------------
        stored = getattr(user, "password_hash", None)
        password_ok = False

        if stored:
            try:
                if isinstance(stored, str) and stored.startswith("$pbkdf2-sha256$"):
                    # סיסמה מוצפנת
                    password_ok = pbkdf2_sha256.verify(password, stored)
                else:
                    # סיסמה רגילה (plain text)
                    password_ok = (password == stored)
            except Exception:
                # אם יש תקלה ב-passlib – נ fallback להשוואה רגילה
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

    except SQLAlchemyError as e:
        # שגיאה במסד נתונים
        current_app.logger.exception("DB error in /api/auth/login: %s", e)
        return jsonify({
            "success": False,
            "message": "שגיאה במסד הנתונים בזמן התחברות"
        }), 500

    except Exception as e:
        # כל שגיאה אחרת – נרשום בלוג וניתן הודעה ברורה
        current_app.logger.exception("Error in /api/auth/login: %s", e)
        return jsonify({
            "success": False,
            "message": f"שגיאה בשרת (login): {str(e)}"
        }), 500
