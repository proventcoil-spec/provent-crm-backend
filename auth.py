# auth.py – מצב פיתוח: כל לוגין מצליח ומחזיר משתמש אדמין קבוע

from flask import Blueprint, request, jsonify, current_app
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
# LOGIN – גרסת DEV: לא בודקים כלום, תמיד מחברים
# --------------------------------------------------
@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    # בקשת OPTIONS (Preflight)
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    # ננסה לקרוא את מה שהפרונט שלח – רק כדי לשמור מייל/יוזר לתצוגה
    data = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip()
    if not identifier:
        identifier = "admin@provent.co.il"

    # יצירת טוקן JWT
    secret = current_app.config.get("JWT_SECRET_KEY", "fallback_jwt_secret")
    payload = {
        "sub": 1,
        "username": "admin.master",
        "role": "owner",
        "full_name": "שלומי פרץ",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    user_data = {
        "id": 1,
        "username": "admin.master",
        "email": identifier,
        "full_name": "שלומי פרץ",
        "role": "owner",
    }

    # תמיד מחזירים success=True
    return jsonify({
        "success": True,
        "message": "התחברת בהצלחה",
        "token": token,
        "user": user_data,
    }), 200
