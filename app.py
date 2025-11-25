
import os
from datetime import datetime, timedelta

from flask import Flask, jsonify
from flask_cors import CORS

from extensions import db
from config import Config
from auth_routes import auth_bp
from clients_routes import clients_bp
from events_routes import events_bp
from leads_routes import leads_bp
from uploads_routes import uploads_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config.get("FRONTEND_ORIGIN", "*")}})

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(leads_bp, url_prefix="/api/leads")
    app.register_blueprint(uploads_bp, url_prefix="/api/uploads")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
