from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import init_db
from auth_routes import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS – פותחים לכל הדומיינים על /api/* כדי שלא תראה שוב שגיאות CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # חיבור DB + יצירת טבלאות + אדמין
    init_db(app)

    # רישום ה-Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
