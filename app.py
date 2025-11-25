
import os
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from passlib.hash import pbkdf2_sha256
import jwt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # ----------------- CONFIG -----------------
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Build from individual env vars if needed
        db_user = os.getenv("DB_USER", "")
        db_pass = os.getenv("DB_PASS", "")
        db_host = os.getenv("DB_HOST", "localhost")
        db_name = os.getenv("DB_NAME", "")
        db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}?charset=utf8mb4"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "Provent-Secret-Key-2025-CRM")

    # CORS – adjust to your domain
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "https://crm.pro-net.pro")
    CORS(app, resources={r"/api/*": {"origins": frontend_origin}})

    db.init_app(app)

    # --------------- MODELS --------------------
    class User(db.Model):
        __tablename__ = "users"

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(255), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(50))
        type = db.Column(db.String(50))
        full_name = db.Column(db.String(255))
        email = db.Column(db.String(255), unique=True)
        phone = db.Column(db.String(20))
        status = db.Column(db.String(20))
        created_at = db.Column(db.DateTime)
        event_role = db.Column(db.String(50))
        payment_type = db.Column(db.String(50))
        payment_amount = db.Column(db.Numeric(10, 2))

    # --------------- ROUTES --------------------

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/api/auth/login", methods=["POST", "OPTIONS"])
    def login():
        # Handle OPTIONS preflight
        if request.method == "OPTIONS":
            return jsonify({"ok": True}), 200

        if not request.is_json:
            return jsonify({"success": False, "error": "Invalid content type"}), 400

        data = request.get_json() or {}

        # Frontend sends email + password
        identifier = (data.get("email") or data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not identifier or not password:
            return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

        # Find user by email or username (case insensitive)
        from sqlalchemy import or_, func

        user = (
            User.query.filter(
                or_(
                    func.lower(User.email) == identifier.lower(),
                    func.lower(User.username) == identifier.lower(),
                )
            )
            .limit(1)
            .first()
        )

        if not user:
            return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

        # Check status if exists
        if user.status and user.status.lower() != "active":
            return jsonify({"success": False, "error": "המשתמש אינו פעיל"}), 401

        # Verify password – first try hash, if fails try plain
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

        # Create JWT
        secret = app.config["JWT_SECRET_KEY"]

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

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
