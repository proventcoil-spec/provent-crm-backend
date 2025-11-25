
from flask import Blueprint, request, jsonify, current_app
from models import User
import jwt
import datetime

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

    data = request.get_json() or {}

    identifier = (data.get("email") or data.get("username") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not identifier or not password:
        return jsonify({
            "success": False,
            "error": "חובה למלא אימייל וסיסמה"
        }), 400

    if "@" in identifier:
        user = User.query.filter(User.email == identifier).first()
    else:
        user = User.query.filter(User.username == identifier).first()

    if not user:
        return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

    if password != (user.password_hash or ""):
        return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

    secret = current_app.config.get("JWT_SECRET_KEY", "fallback_jwt_secret")
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
            "status": user.status,
        }
    }), 200
    from passlib.hash import pbkdf2_sha256
from models import User, db  # ודא שזה כבר קיים אצלך (כמו בשאר הראוטים)

@auth_bp.route('/seed-admin', methods=['POST'])
def seed_admin():
    # כדי שלא ניצור פעמיים
    if User.query.filter_by(email="admin@provent.co.il").first():
        return jsonify({"message": "admin already exists"}), 400

    password = "Provent-2025!crm"  # סיסמה זמנית, תחליף אחרי שתיכנס
    password_hash = pbkdf2_sha256.hash(password)

    admin = User(
        email="admin@provent.co.il",
        password_hash=password_hash,
        role="owner",
        full_name="שלומי פרץ",
        status="active"
    )
    db.session.add(admin)
    db.session.commit()

    return jsonify({"message": "admin created", "email": admin.email, "password": password}), 201
