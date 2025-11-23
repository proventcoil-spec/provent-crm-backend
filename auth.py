from datetime import datetime, timedelta
import os
import jwt
from flask import Blueprint, request, jsonify, current_app
from passlib.hash import pbkdf2_sha256
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.system_role,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "חסר שם משתמש או סיסמה"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not pbkdf2_sha256.verify(password, user.password_hash):
        return jsonify({"error": "שם משתמש או סיסמה שגויים"}), 401

    token = create_token(user)
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "role": user.system_role,
        }
    })

@auth_bp.route("/me", methods=["GET"])
def me():
    # כרגע רק מחזיר OK – אפשר להרחיב לפיענוח JWT אם הפרונט ישלח Authorization
    return jsonify({"status": "ok"})
