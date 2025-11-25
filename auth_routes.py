from flask import Blueprint, jsonify, request
from extensions import db
from models import User
from passlib.hash import bcrypt
import jwt
import os
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/seed-admin", methods=["POST"])
def seed_admin():
    admin = User.query.filter_by(email="admin@provent.co.il").first()
    if admin:
        return jsonify({"msg": "Admin already exists"})

    admin = User(
        email="admin@provent.co.il",
        full_name="Admin",
        role="owner",
        password_hash=bcrypt.hash("Provent-2025!crm")
    )
    db.session.add(admin)
    db.session.commit()
    return jsonify({"msg": "Admin created"})
