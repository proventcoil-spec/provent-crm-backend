
from flask import Blueprint, request, jsonify
from extensions import db
from models import Lead

leads_bp = Blueprint("leads_bp", __name__)


@leads_bp.route("/", methods=["GET"])
def list_leads():
    q = Lead.query.order_by(Lead.created_at.desc()).all()
    items = []
    for l in q:
        items.append({
            "id": l.id,
            "full_name": l.full_name,
            "phone": l.phone,
            "email": l.email,
            "source": l.source,
            "event_type": l.event_type,
            "event_date": l.event_date.isoformat() if l.event_date else None,
            "status": l.status,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        })
    return jsonify({"success": True, "items": items})


@leads_bp.route("/", methods=["POST"])
def create_lead():
    data = request.get_json() or {}
    full_name = (data.get("full_name") or "").strip()
    if not full_name:
        return jsonify({"success": False, "error": "חובה שם ללקוח פוטנציאלי"}), 400

    lead = Lead(
        full_name=full_name,
        phone=data.get("phone"),
        email=data.get("email"),
        source=data.get("source"),
        event_type=data.get("event_type"),
        notes=data.get("notes"),
    )
    db.session.add(lead)
    db.session.commit()
    return jsonify({"success": True, "id": lead.id}), 201
