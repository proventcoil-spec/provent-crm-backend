# app.py
from flask import Flask

from extensions import init_db
from auth_routes import auth_bp
from clients_routes import clients_bp
from events_routes import events_bp
from leads_routes import leads_bp
from uploads_routes import uploads_bp


def create_app():
    app = Flask(__name__)

    # DB + CORS
    init_db(app)

    # רישום ראוטים
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(leads_bp, url_prefix="/api/leads")
    app.register_blueprint(uploads_bp, url_prefix="/api/uploads")

    return app


# עבור gunicorn ברנדר
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
