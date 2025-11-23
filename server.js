from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import timedelta
import os


def create_app():
    app = Flask(__name__)

    # --- CORS מלא ללא מגבלות (לפתור סופית את הבעיה) ---
    CORS(app,
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # --- קונפיג בסיסי ---
    app.config["JSON_AS_ASCII"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "DEV_SECRET")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "DEV_JWT")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    # --- ROUTE בריאות מערכת ---
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # --- LOGIN לדוגמה (תתאים למסד נתונים שלך) ---
    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"success": False, "error": "Missing fields"}), 400

        # תבדוק במסד הנתונים פה
        return jsonify({
            "success": True,
            "token": "demo_token",
            "username": username,
            "role": "owner",
            "fullName": "שלומי פרץ"
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
