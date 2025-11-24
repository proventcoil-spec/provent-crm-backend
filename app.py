from flask import Flask, request, jsonify
from flask_cors import CORS
import MySQLdb.cursors
import bcrypt
import jwt
import datetime
import os

app = Flask(__name__)

# ---------- CONFIG ----------
app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASS")
app.config['MYSQL_DB'] = os.getenv("DB_NAME")
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

SECRET_KEY = os.getenv("SECRET_KEY")


CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------- HEALTH ----------
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200


# ---------- LOGIN ----------
@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"success": False, "error": "Missing username or password"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s LIMIT 1", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 401

        # check hash
        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return jsonify({"success": False, "error": "Wrong password"}), 401

        token = jwt.encode(
            {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({
            "success": True,
            "token": token,
            "username": user["username"],
            "role": user["role"],
            "fullName": user["full_name"]
        })

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"success": False, "error": "Server error"}), 500


# ---------- START ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
