import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import jwt
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# ------------------ CONFIG ------------------
app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASS")
app.config['MYSQL_DB'] = os.getenv("DB_NAME")
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

SECRET_KEY = os.getenv("SECRET_KEY")

CORS(app, resources={r"/api/*": {"origins": "*"}})

# ------------------ HEALTH CHECK ------------------
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

# ------------------ LOGIN ------------------
@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"success": False, "error": "Missing username or password"}), 400

        cursor = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        ).cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s LIMIT 1", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 401

        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return jsonify({"success": False, "error": "Incorrect password"}), 401

        token = jwt.encode(
            {"id": user["id"], "username": user["username"]},
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({
            "success": True,
            "token": token,
            "username": user["username"],
            "full_name": user.get("full_name", "")
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
