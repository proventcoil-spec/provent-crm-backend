# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
from models import db, User
from auth import auth_bp
from events import events_bp
from clients import clients_bp
from workers_routes import workers_bp
from leads_bp import leads_bp
from settings_routes import settings_bp


def create_app():
    app = Flask(__name__)

    # טוען הגדרות (DB, SECRET_KEY, JWT וכו') מתוך config.py וה־env של Render
    app.config.from_object(get_config())

    # חיבור SQLAlchemy
    db.init_app(app)

    # CORS – מאפשר גישה מהדומיין של ה־CRM ומהכל (למקרה הצורך)
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True
    )

    # רישום כל ה־Blueprints עם prefix של /api
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(workers_bp, url_prefix="/api/workers")
    app.register_blueprint(leads_bp, url_prefix="/api/leads")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")

    # בדיקת חיים לשרת (זה מה שעובד לך כרגע)
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    return app


# האובייקט ש-gunicorn משתמש בו
app = create_app()

if __name__ == "__main__":
    # להרצה לוקאלית
    app.run(host="0.0.0.0", port=5000)
