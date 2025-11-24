# auth.py – לוגין אמיתי מול DB

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
# LOGIN – אימות אמיתי מול טבלת users
# --------------------------------------------------
@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    # בקשת OPTIONS (Preflight)
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        # קוראים את הנתונים שנשלחו מהפרונט
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict() or {}

        # הפרונט שלך יכול לקרוא לזה username או email – נתפוס את שניהם
        identifier = (
            data.get("username")
            or data.get("email")
            or data.get("user")
            or data.get("login")
            or ""
        ).strip()

        password = (data.get("password") or data.get("pass") or "").strip()

        if not identifier or not password:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        identifier_lower = identifier.lower()

        # מחפשים משתמש לפי username או email
        user = (
            User.query.filter(
                or_(
                    db.func.lower(User.username) == identifier_lower,
                    db.func.lower(User.email) == identifier_lower,
                )
            )
            .limit(1)
            .first()
        )

        if not user:
            current_app.logger.warning(
                f"LOGIN FAILED: user not found for identifier='{identifier_lower}'"
            )
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        # אם יש סטטוס – נוודא שהוא active
        user_status = getattr(user, "status", "active")
        if user_status and user_status.lower() != "active":
            current_app.logger.warning(
                f"LOGIN FAILED: user '{user.username}' is not active (status={user_status})"
            )
            return jsonify({
                "success": False,
                "message": "המשתמש אינו פעיל"
            }), 401

        # בדיקת סיסמה
        stored_password = getattr(user, "password_hash", None)
        password_ok = False

        try:
            if isinstance(stored_password, str) and stored_password.startswith(
                "$pbkdf2-sha256$"
            ):
                # סיסמה מוצפנת
                password_ok = pbkdf2_sha256.verify(password, stored_password)
            else:
                # טקסט רגיל
                password_ok = (password == stored_password)
        except Exception as e:
            current_app.logger.exception(
                f"LOGIN ERROR: problem verifying password for user '{user.username}': {e}"
            )
            password_ok = False

        if not password_ok:
            current_app.logger.warning(
                f"LOGIN FAILED: wrong password for user '{user.username}'"
            )
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        # ------------------------------
        # אם הגענו לכאן – הלוגין הצליח
        # ------------------------------
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
