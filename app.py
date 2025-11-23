# app.py
from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config
from models import db, User
from auth import auth_bp
from events import events_bp
from clients import clients_bp
from workers_routes import workers_bp
from leads import leads_bp
from settings_routes import settings_bp


def create_app():
    app = Flask(__name__)

    # טעינת הגדרות (DB וכו') מתוך config.py
    app.config.from_object(get_config())

    # חיבור SQLAlchemy
    db.init_app(app)

    # ---- הגדרת CORS כך שהדפדפן יוכל לגשת מה-CRM ----
    CORS(
        app,
        resources={r"/api/*": {
            "origins": [
                "https://crm.pro-net.pro",
                "http://crm.pro-net.pro",
                "https://www.crm.pro-net.pro"
            ]
        }},
        supports_credentials=True
    )

    @app.after_request
    def add_cors_headers(response):
        # כותרות CORS לכל תגובה
        response.headers["Access-Control-Allow-Origin"] = "https://crm.pro-net.pro"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    # ---- טיפול ב-OPTIONS כדי שה-preflight לא ייפול ----
    @app.route("/api/auth/login", methods=["OPTIONS"])
    def login_options():
        return ("", 204)

    # אפשר להוסיף כאן OPTIONS נוספים אם צריך:
    # @app.route("/api/clients", methods=["OPTIONS"])
    # def clients_options():
    #     return ("", 204)

    # ---- רישום כל ה-BLUEPRINTS ----
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(workers_bp, url_prefix="/api/workers")
    app.register_blueprint(leads_bp, url_prefix="/api/leads")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")

    # ---- בדיקת חיים ----
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


# להרצה לוקלית, וברנדר משתמש בזה דרך gunicorn
if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000)
