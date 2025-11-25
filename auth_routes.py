
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_, func
from passlib.hash import pbkdf2_sha256
import jwt

from extensions import db
from models import User

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = current_app.config.get("FRONTEND_ORIGIN", "*")
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict() or {}

    identifier = (data.get("email") or data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not identifier or not password:
        return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

    ident_lower = identifier.lower()

    user = (
        User.query.filter(
            func.lower(User.email) == ident_lower
        )
        .limit(1)
        .first()
    )
    if not user:
        user = (
            User.query.filter(
                func.lower(User.username) == ident_lower
            )
            .limit(1)
            .first()
        )

    if not user:
        return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

    if user.status and user.status.lower() != "active":
        return jsonify({"success": False, "error": "המשתמש אינו פעיל"}), 401

    stored = user.password_hash or ""
    ok = False
    try:
        if stored.startswith("$pbkdf2-sha256$") or stored.startswith("pbkdf2_sha256$"):
            ok = pbkdf2_sha256.verify(password, stored)
        else:
            ok = password == stored
    except Exception:
        ok = False

    if not ok:
        return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

    secret = current_app.config["JWT_SECRET_KEY"]
    payload = {
        "sub": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
        "exp": datetime.utcnow() + timedelta(hours=12),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify(
        {
            "success": True,
            "message": "התחברת בהצלחה",
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
            },
        }
    ), 200
