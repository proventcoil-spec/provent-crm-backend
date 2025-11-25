
from datetime import datetime

from flask import Blueprint, request, jsonify
from extensions import db
from models import Event, Client

events_bp = Blueprint("events_bp", __name__)

@events_bp.route("/", methods=["GET"])
def list_events():
    q = Event.query.order_by(Event.date.asc()).all()
    items = []
    for e in q:
        items.append({
            "id": e.id,
            "name": e.name,
            "type": e.type,
            "date": e.date.isoformat() if e.date else None,
            "location": e.location,
            "status": e.status,
            "client": {
                "id": e.client.id,
                "full_name": e.client.full_name,
            } if e.client else None,
        })
    return jsonify({"success": True, "items": items})

@events_bp.route("/", methods=["POST"])
def create_event():
    data = request.get_json() or {}
    client_id = data.get("client_id")
    name = (data.get("name") or "").strip()
    if not client_id or not name:
        return jsonify({"success": False, "error": "חסר לקוח או שם אירוע"}), 400

    client = Client.query.get(client_id)
    if not client:
        return jsonify({"success": False, "error": "לקוח לא נמצא"}), 404

    date_str = data.get("date")
    date_val = None
    if date_str:
        try:
            date_val = datetime.fromisoformat(date_str).date()
        except ValueError:
            pass

    ev = Event(
        client=client,
        name=name,
        type=data.get("type"),
        date=date_val,
        location=data.get("location"),
        guests_count=data.get("guests_count"),
        status=data.get("status") or "פתוח",
        budget=data.get("budget"),
    )
    db.session.add(ev)
    db.session.commit()

    return jsonify({"success": True, "id": ev.id}), 201

@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    e = Event.query.get_or_404(event_id)
    data = {
        "id": e.id,
        "name": e.name,
        "type": e.type,
        "date": e.date.isoformat() if e.date else None,
        "location": e.location,
        "guests_count": e.guests_count,
        "status": e.status,
        "budget": float(e.budget) if e.budget is not None else None,
        "client": {
            "id": e.client.id,
            "full_name": e.client.full_name,
            "phone": e.client.phone,
            "email": e.client.email,
        } if e.client else None,
    }
    return jsonify({"success": True, "event": data})
