from flask import Flask, jsonify, request
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


# =========================================
# יצירת האפליקציה
# =========================================
def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # הרשאות קרוס-דומיין ל־/api
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # חיבור SQLAlchemy
    db.init_app(app)

    # רישום כל ה־Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(events_bp, url_prefix="/api")
    app.register_blueprint(clients_bp, url_prefix="/api")
    app.register_blueprint(workers_bp, url_prefix="/api")
    app.register_blueprint(leads_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")

    # ===== בריאות שרת =====
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # ===== פונקציה פנימית שמאתחלת את ה־DB ומכניסה משתמשי ברירת מחדל =====
    def init_db_with_defaults():
        """
        מוחקת את כל הטבלאות, יוצרת מחדש, ומכניסה את שלומי ושמעון כבעלי מערכת.
        להפעיל רק כשאנחנו יודעים מה עושים (מאפס את הכל).
        """
        with app.app_context():
            db.drop_all()
            db.create_all()

            # בדיקה אם המשתמשים כבר קיימים – כדי לא ליצור כפולים
            existing_shlomi = User.query.filter_by(username="shlomi").first()
            existing_shimon = User.query.filter_by(username="shimon").first()

            if not existing_shlomi:
                owner1 = User(
                    full_name="שלומי פרץ",
                    phone="050-0000000",
                    email="",
                    username="shlomi",
                    password_hash=pbkdf2_sha256.hash("1234"),
                    type="employee",
                    system_role="owner",
                    event_role="מנהל ראשי",
                    status="active",
                    internal_notes="50% שותף ברווח"
                )
                db.session.add(owner1)

            if not existing_shimon:
                owner2 = User(
                    full_name="שמעון אסרף",
                    phone="052-1111111",
                    email="",
                    username="shimon",
                    password_hash=pbkdf2_sha256.hash("1234"),
                    type="employee",
                    system_role="owner",
                    event_role="מנהל ראשי",
                    status="active",
                    internal_notes="50% שותף ברווח"
                )
                db.session.add(owner2)

            db.session.commit()
            print("DB initialized with default owners (shlomi/shimon, password 1234).")

    # ===== פקודת CLI – למקרה שתריץ מקומית (לא חובה ברנדר חינמי) =====
    @app.cli.command("init-db")
    def init_db_command():
        """איתחול בסיס הנתונים + משתמשי ברירת מחדל (שלומי / שמעון)."""
        init_db_with_defaults()

    # ===== API סודי לאיתחול DB מרנדר =====
    @app.route("/api/init-db-once")
    def http_init_db():
        """
        קריאה לכתובת:
        /api/init-db-once?secret=provent123

        מאפסת את בסיס הנתונים ומכניסה את משתמשי ברירת המחדל.
        אל תשתמש בזה ביום-יום. רק בהקמה / ריסט.
        """
        secret = request.args.get("secret")
        # אתה יכול להחליף את המחרוזת "provent123" לסיסמה אחרת
        if secret != "provent123":
            return jsonify({"error": "forbidden"}), 403

        init_db_with_defaults()
        return jsonify({"status": "db initialized"}), 200

    return app


# Flask application object ש־gunicorn משתמש בו
app = create_app()

if __name__ == "__main__":
    # להרצה מקומית
    app.run(host="0.0.0.0", port=5000)
