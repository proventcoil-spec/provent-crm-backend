from flask import Blueprint, request, jsonify
from passlib.hash import pbkdf2_sha256
from models import db, User

workers_bp = Blueprint("workers", __name__, url_prefix="/api/workers")

def worker_to_dict(w: User):
    return {
        "id": w.id,
        "full_name": w.full_name,
        "type": w.type,
        "system_role": w.system_role,
        "event_role": w.event_role,
        "phone": w.phone,
        "email": w.email,
        "status": w.status,
        "username": w.username,
        "payment_type": w.payment_type,
        "payment_amount": w.payment_amount,
        "internal_notes": w.internal_notes,
        "notes": w.notes,
    }

@workers_bp.route("", methods=["GET"])
def list_workers():
    workers = User.query.order_by(User.full_name.asc()).all()
    return jsonify([worker_to_dict(w) for w in workers])

@workers_bp.route("", methods=["POST"])
def create_worker():
    data = request.get_json() or {}
    if not data.get("full_name") or not data.get("phone") or not data.get("username") or not data.get("password"):
        return jsonify({"error": "חסר שם, טלפון, יוזר או סיסמה"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "שם משתמש תפוס"}), 400

    w = User(
        full_name=data["full_name"],
        phone=data["phone"],
        email=data.get("email"),
        username=data["username"],
        password_hash=pbkdf2_sha256.hash(data["password"]),
        type=data.get("type", "employee"),
        system_role=data.get("system_role", "worker"),
        event_role=data.get("event_role"),
        status=data.get("status", "active"),
        payment_type=data.get("payment_type"),
        payment_amount=data.get("payment_amount"),
        internal_notes=data.get("internal_notes"),
        notes=data.get("notes"),
    )
    db.session.add(w)
    db.session.commit()
    return jsonify(worker_to_dict(w)), 201

@workers_bp.route("/<int:worker_id>", methods=["PUT"])
def update_worker(worker_id):
    w = User.query.get_or_404(worker_id)
    data = request.get_json() or {}
    w.full_name = data.get("full_name", w.full_name)
    w.phone = data.get("phone", w.phone)
    w.email = data.get("email", w.email)
    w.type = data.get("type", w.type)
    w.system_role = data.get("system_role", w.system_role)
    w.event_role = data.get("event_role", w.event_role)
    w.status = data.get("status", w.status)
    w.payment_type = data.get("payment_type", w.payment_type)
    w.payment_amount = data.get("payment_amount", w.payment_amount)
    w.internal_notes = data.get("internal_notes", w.internal_notes)
    w.notes = data.get("notes", w.notes)

    if data.get("password"):
        w.password_hash = pbkdf2_sha256.hash(data["password"])

    db.session.commit()
    return jsonify(worker_to_dict(w))

@workers_bp.route("/<int:worker_id>", methods=["DELETE"])
def delete_worker(worker_id):
    w = User.query.get_or_404(worker_id)
    db.session.delete(w)
    db.session.commit()
    return jsonify({"ok": True})
