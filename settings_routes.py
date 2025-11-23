from flask import Blueprint, request, jsonify
from models import db, BusinessSettings, ContractTemplate, Category
from datetime import datetime

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")

# ----- Business -----
@settings_bp.route("/business", methods=["GET"])
def get_business():
    biz = BusinessSettings.query.first()
    if not biz:
        return jsonify({})
    return jsonify({
        "name": biz.name,
        "legal_name": biz.legal_name,
        "phone": biz.phone,
        "email": biz.email,
        "whatsapp": biz.whatsapp,
        "address": biz.address,
        "city": biz.city,
        "website": biz.website,
        "logo_url": biz.logo_url,
        "sms_sender": biz.sms_sender,
    })

@settings_bp.route("/business", methods=["PUT", "POST"])
def save_business():
    data = request.get_json() or {}
    biz = BusinessSettings.query.first()
    if not biz:
        biz = BusinessSettings()
        db.session.add(biz)
    biz.name = data.get("name")
    biz.legal_name = data.get("legal_name")
    biz.phone = data.get("phone")
    biz.email = data.get("email")
    biz.whatsapp = data.get("whatsapp")
    biz.address = data.get("address")
    biz.city = data.get("city")
    biz.website = data.get("website")
    biz.logo_url = data.get("logo_url")
    biz.sms_sender = data.get("sms_sender")
    db.session.commit()
    return jsonify({"ok": True})

# ----- Contract templates -----
@settings_bp.route("/contracts", methods=["GET"])
def list_contracts():
    templates = ContractTemplate.query.order_by(ContractTemplate.updated_at.desc()).all()
    return jsonify([
        {
            "id": t.id,
            "name": t.name,
            "type": t.type,
            "content": t.content,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }
        for t in templates
    ])

@settings_bp.route("/contracts", methods=["POST"])
def save_contract():
    data = request.get_json() or {}
    tpl_id = data.get("id")
    if tpl_id:
        t = ContractTemplate.query.get_or_404(tpl_id)
    else:
        t = ContractTemplate()
        db.session.add(t)
    t.name = data.get("name")
    t.type = data.get("type", "event")
    t.content = data.get("content", "")
    t.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True, "id": t.id})

@settings_bp.route("/contracts/<int:tpl_id>", methods=["DELETE"])
def delete_contract(tpl_id):
    t = ContractTemplate.query.get_or_404(tpl_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"ok": True})

# ----- Categories -----
@settings_bp.route("/categories", methods=["GET"])
def list_categories():
    cats = Category.query.order_by(Category.name.asc()).all()
    return jsonify([
        {"id": c.id, "name": c.name, "type": c.type}
        for c in cats
    ])

@settings_bp.route("/categories", methods=["POST"])
def save_category():
    data = request.get_json() or {}
    cat_id = data.get("id")
    if cat_id:
        c = Category.query.get_or_404(cat_id)
    else:
        c = Category()
        db.session.add(c)
    c.name = data.get("name")
    c.type = data.get("type", "event_service")
    db.session.commit()
    return jsonify({"ok": True, "id": c.id})

@settings_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
def delete_category(cat_id):
    c = Category.query.get_or_404(cat_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"ok": True})
