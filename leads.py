from flask import Blueprint, request, jsonify
from models import db, Lead

leads_bp = Blueprint("leads", __name__, url_prefix="/api/leads")

def lead_to_dict(l: Lead):
    return {
        "id": l.id,
        "full_name": l.full_name,
        "phone": l.phone,
        "email": l.email,
        "source": l.source,
        "notes": l.notes,
        "status": l.status,
    }

@leads_bp.route("", methods=["GET"])
def list_leads():
    q = Lead.query.order_by(Lead.created_at.desc())
    status = request.args.get("status")
    if status:
        q = q.filter(Lead.status == status)
    return jsonify([lead_to_dict(l) for l in q.all()])

@leads_bp.route("", methods=["POST"])
def create_lead():
    data = request.get_json() or {}
    l = Lead(
        full_name=data.get("full_name"),
        phone=data.get("phone"),
        email=data.get("email"),
        source=data.get("source"),
        notes=data.get("notes"),
        status=data.get("status", "חדש"),
    )
    db.session.add(l)
    db.session.commit()
    return jsonify(lead_to_dict(l)), 201

@leads_bp.route("/<int:lead_id>", methods=["PUT"])
def update_lead(lead_id):
    l = Lead.query.get_or_404(lead_id)
    data = request.get_json() or {}
    l.full_name = data.get("full_name", l.full_name)
    l.phone = data.get("phone", l.phone)
    l.email = data.get("email", l.email)
    l.source = data.get("source", l.source)
    l.notes = data.get("notes", l.notes)
    l.status = data.get("status", l.status)
    db.session.commit()
    return jsonify(lead_to_dict(l))
