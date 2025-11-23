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
from passlib.hash import pbkdf2_sha256

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # CORS – לאפשר גישה מהדומיין שלך
    CORS(app, resources={r"/api/*": {"origins": ["*"]}})

    db.init_app(app)

    # רישום בלופרינטים
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(workers_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(settings_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.cli.command("init-db")
    def init_db_command():
        """יצירת טבלאות ויוזרים ראשונים (שלומי + שמעון)."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            # יוזרים ראשונים
            owner1 = User(
                full_name="שלומי פרץ",
                phone="050-0000000",
                email="",
                username="shlomi",
                password_hash=pbkdf2_sha256.hash("1234"),  # להחליף אחרי ההתקנה
                type="employee",
                system_role="owner",
                event_role="הפקת אירוע",
                status="active",
                internal_notes="מייסד שותף | 50%")

            owner2 = User(
                full_name="שמעון אסרף",
                phone="050-1111111",
                email="",
                username="shimon",
                password_hash=pbkdf2_sha256.hash("1234"),  # להחליף אחרי ההתקנה
                type="employee",
                system_role="owner",
                event_role="הפקת אירוע",
                status="active",
                internal_notes="מייסד שותף | 50%")

            db.session.add_all([owner1, owner2])
            db.session.commit()
            print("DB initialized with default owners (shlomi/shimon, password 1234).")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
