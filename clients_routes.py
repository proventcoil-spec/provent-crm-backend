
from flask import Blueprint, request, jsonify
from extensions import db
from models import Client, Event

clients_bp = Blueprint("clients_bp", __name__)

@clients_bp.route("/", methods=["GET"])
def list_clients():
    q = Client.query.order_by(Client.created_at.desc()).all()
    data = []
    for c in q:
        data.append({
            "id": c.id,
            "full_name": c.full_name,
            "phone": c.phone,
            "email": c.email,
            "city": c.city,
            "events_count": len(c.events),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return jsonify({"success": True, "items": data})

@clients_bp.route("/", methods=["POST"])
def create_client():
    data = request.get_json() or {}
    full_name = (data.get("full_name") or "").strip()
    if not full_name:
        return jsonify({"success": False, "error": "חובה שם לקוח"}), 400

    client = Client(
        full_name=full_name,
        phone=data.get("phone"),
        email=data.get("email"),
        city=data.get("city"),
        notes=data.get("notes"),
    )
    db.session.add(client)
    db.session.commit()

    return jsonify({"success": True, "id": client.id}), 201

@clients_bp.route("/<int:client_id>", methods=["GET"])
def get_client(client_id):
    c = Client.query.get_or_404(client_id)
    events_data = []
    for e in c.events:
        events_data.append({
            "id": e.id,
            "name": e.name,
            "type": e.type,
            "date": e.date.isoformat() if e.date else None,
            "location": e.location,
            "status": e.status,
        })
    data = {
        "id": c.id,
        "full_name": c.full_name,
        "phone": c.phone,
        "email": c.email,
        "city": c.city,
        "notes": c.notes,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "events": events_data,
    }
    return jsonify({"success": True, "client": data})
