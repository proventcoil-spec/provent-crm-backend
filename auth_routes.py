from flask import Blueprint, request, jsonify
from models import User

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "חסר אימייל או סיסמה"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "שם משתמש או סיסמה לא נכונים"}), 401

    # לא משתמשים כרגע ב-JWT – רק מחזירים תשובה מוצלחת
    return jsonify({
        "message": "התחברות הצליחה",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
        "token": "dummy-token"  # אם הפרונט מצפה לאיזה שדה token
    }), 200
