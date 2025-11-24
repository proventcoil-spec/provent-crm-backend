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
# פונקציה עזר ליצירת JWT + אובייקט משתמש להחזיר לפרונט
# --------------------------------------------------
def build_login_response(user_id, username, email, full_name, role):
    secret = current_app.config.get("JWT_SECRET_KEY", "fallback_jwt_secret")

    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "full_name": full_name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    user_data = {
        "id": user_id,
        "username": username,
        "email": email,
        "full_name": full_name,
        "role": role,
    }

    return jsonify({
        "success": True,
        "message": "התחברת בהצלחה",
        "token": token,
        "user": user_data,
    }), 200


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

        # בטופס יש רק אימייל, אבל הפרונט שולח אותו בתור "username"
        identifier = (data.get("username") or data.get("email") or "").strip()
        password = (data.get("password") or "").strip()

        if not identifier or not password:
            return jsonify({
                "success": False,
                "message": "שם המשתמש או הסיסמה לא נכונים"
            }), 401

        # =======================
        # 1. ניסיון התחברות מול DB
        # =======================
        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()

        if user:
            # בדיקת סיסמה: hash או טקסט רגיל
            stored = getattr(user, "password_hash", None)
            password_ok = False

            try:
                if isinstance(stored, str) and stored.startswith("$pbkdf2-sha256$"):
                    password_ok = pbkdf2_sha256.verify(password, stored)
                else:
                    password_ok = (password == stored)
            except Exception:
                password_ok = (password == stored)

            if password_ok:
                # התחברות תקינה דרך DB
                return build_login_response(
                user_id=user.id,
                username=user.username,
                email=getattr(user, "email", None),
                full_name=getattr(user, "full_name", None),
                role=getattr(user, "role", None),
            )

        # =======================
        # 2. Fallback קשיח למשתמש admin
        #    גם אם ה-DB לא מסתדר, אבל המייל והסיסמה תואמים –
        #    נחבר אותך בכל מקרה.
        # =======================
        fallback_email = "admin@provent.co.il"
        fallback_password = "Provent-2025"

        if identifier.lower() == fallback_email.lower() and password == fallback_password:
            current_app.logger.warning(
                "LOGIN FALLBACK: logging in hard-coded admin (DB login failed or mismatched)"
            )
            return build_login_response(
                user_id=1,
                username="admin.master",
                email=fallback_email,
                full_name="שלומי - Admin",
                role="owner",
            )

        # אם לא DB ולא fallback – מחזירים שגיאה רגילה
        return jsonify({
            "success": False,
            "message": "שם המשתמש או הסיסמה לא נכונים"
        }), 401

    except Exception as e:
        current_app.logger.exception("Error in /api/auth/login: %s", e)
        return jsonify({
            "success": False,
            "message": "שגיאה בשרת בזמן התחברות"
        }), 500
