# auth.py
from flask import Blueprint, request, jsonify, current_app
from models import db, User
from passlib.hash import pbkdf2_sha256
import jwt
import datetime

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.after_request
def add_cors_headers(response):
    """
    מוסיף כותרות CORS לכל תגובה שיוצאת מה-auth
    כדי ש-crm.pro-net.pro יוכל לדבר עם השרת בלי חסימה.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    # CORS / Preflight
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username or not password:
            return jsonify({"success": False, "message": "שם משתמש או סיסמה חובה"}), 400

        # חיפוש משתמש לפי username (אצלך זה המייל שאתה מזין במסך)
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"success": False, "message": "משתמש לא נמצא"}), 401

        # בדיקת סיסמה (מוצפנת עם pbkdf2_sha256)
        if not pbkdf2_sha256.verify(password, user.password):
            return jsonify({"success": False, "message": "סיסמה שגויה"}), 401

        # JWT
        secret = current_app.config.get("JWT_SECRET_KEY", "fallback_jwt_secret")
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        user_data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
        }

        return jsonify({
            "success": True,
            "message": "התחברת בהצלחה",
            "token": token,
            "user": user_data,
        }), 200

    except Exception as e:
        # לוג מפורט ברנדר
        current_app.logger.exception("Error in /api/auth/login: %s", e)
        # מחזירים ללקוח את הטעות האמיתית (כדי שנוכל לאתר)
        return jsonify({
            "success": False,
            "message": f"שגיאה בשרת (login): {str(e)}"
        }), 500
