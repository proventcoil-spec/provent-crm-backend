import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import jwt

# ------------ APP ------------

app = Flask(__name__)

# ------------ CONFIG FROM ENV ------------

app.config["MYSQL_HOST"] = os.getenv("DB_HOST")
app.config["MYSQL_USER"] = os.getenv("DB_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("DB_PASS")
app.config["MYSQL_DB"] = os.getenv("DB_NAME")

SECRET_KEY = os.getenv("SECRET_KEY", "Provent-Secret-Key-2025-CRM")

CORS(app, resources={r"/api/*": {"origins": "*"}})


# DB HELPER
def get_connection():
    return pymysql.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        db=app.config["MYSQL_DB"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=10,
        read_timeout=20,
        write_timeout=20,
    )

# ------------ HEALTH CHECK ------------

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200


# ------------ LOGIN ------------

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return jsonify({"success": False, "error": "חובה למלא שם משתמש וסיסמה"}), 400

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT id, username, password_hash, role, full_name
                    FROM users
                    WHERE username = %s
                    LIMIT 1
                """
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
        finally:
            conn.close()

        if not user:
            return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

        # כרגע השוואה פשוטה (בלי הצפנה) כדי ש*יעבוד*:
        if password != user["password_hash"]:
            return jsonify({"success": False, "error": "שם משתמש או סיסמה לא נכונים"}), 401

        payload = {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "fullName": user.get("full_name") or "",
            "exp": datetime.utcnow().timestamp() + 60 * 60 * 8,  # תוקף 8 שעות
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "success": True,
            "token": token,
            "username": user["username"],
            "role": user["role"],
            "fullName": user.get("full_name") or "",
        }), 200

    except Exception as e:
        # לוג מפורט ל-Render כדי שאפשר להבין 500 אם יהיה
        print("LOGIN ERROR:", repr(e))
        return jsonify({"success": False, "error": "שגיאה בשרת (login)"}), 500


# ------------ MAIN (LOCAL) ------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
