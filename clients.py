from flask import Blueprint, request, jsonify
from models import db, Client

clients_bp = Blueprint("clients", __name__, url_prefix="/api/clients")

def client_to_dict(c: Client):
    return {
        "id": c.id,
        "full_name": c.full_name,
        "phone": c.phone,
        "email": c.email,
        "notes": c.notes,
    }

@clients_bp.route("", methods=["GET"])
def list_clients():
    q = Client.query.order_by(Client.created_at.desc())
    search = request.args.get("q")
    if search:
        q = q.filter(Client.full_name.ilike(f"%{search}%"))
    return jsonify([client_to_dict(c) for c in q.all()])

@clients_bp.route("", methods=["POST"])
def create_client():
    data = request.get_json() or {}
    if not data.get("full_name") or not data.get("phone"):
        return jsonify({"error": "שם וטלפון חובה"}), 400
    c = Client(
        full_name=data["full_name"],
        phone=data["phone"],
        email=data.get("email"),
        notes=data.get("notes"),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(client_to_dict(c)), 201

@clients_bp.route("/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    c = Client.query.get_or_404(client_id)
    data = request.get_json() or {}
    c.full_name = data.get("full_name", c.full_name)
    c.phone = data.get("phone", c.phone)
    c.email = data.get("email", c.email)
    c.notes = data.get("notes", c.notes)
    db.session.commit()
    return jsonify(client_to_dict(c))
