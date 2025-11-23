import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --------------------------
# CONFIG
# --------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "provent-secret")
db = SQLAlchemy(app)

# --------------------------
#  CORS – פתוח רק לדומיין שלך
# --------------------------
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "https://crm.pro-net.pro",
        "http://crm.pro-net.pro"
    ]}},
    supports_credentials=True
)


# --------------------------
# ROUTES בסיסיים
# --------------------------
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200


# --------------------------
# MAIN – Render מחייב להשתמש ב־PORT מה־ENV
# --------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
