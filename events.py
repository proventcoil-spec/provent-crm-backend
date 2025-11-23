from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Client, Event, EventWorker, EventMeeting

events_bp = Blueprint("events", __name__, url_prefix="/api/events")

def event_to_dict(ev: Event):
    return {
        "id": ev.id,
        "client_id": ev.client_id,
        "client_name": ev.client.full_name if ev.client else None,
        "client_phone": ev.client.phone if ev.client else None,
        "date": ev.date.isoformat() if ev.date else None,
        "type": ev.type,
        "location": ev.location,
        "celebrant": ev.celebrant,
        "tz": ev.tz,
        "status": ev.status,
        "details": ev.details,
        "categories": ev.categories,
        "price": ev.price,
        "deposit": ev.deposit,
        "deposit_to": ev.deposit_to,
        "expenses": ev.expenses,
        "workers": [
            {
                "id": w.id,
                "name": w.name,
                "category": w.category,
                "amount": w.amount,
                "note": w.note,
            } for w in ev.workers
        ],
        "meetings": [
            {
                "id": m.id,
                "type": m.type,
                "date": m.date,
                "time": m.time,
                "location": m.location,
            } for m in ev.meetings
        ],
    }

@events_bp.route("", methods=["GET"])
def list_events():
    date = request.args.get("date")
    client = request.args.get("client")
    location = request.args.get("location")

    q = Event.query.join(Client)
    if date:
        try:
            d_obj = datetime.fromisoformat(date).date()
            q = q.filter(Event.date == d_obj)
        except ValueError:
            pass
    if client:
        q = q.filter(Client.full_name.ilike(f"%{client}%"))
    if location:
        q = q.filter(Event.location.ilike(f"%{location}%"))

    events = q.order_by(Event.date.desc()).all()
    return jsonify([event_to_dict(ev) for ev in events])

@events_bp.route("", methods=["POST"])
def create_event():
    data = request.get_json() or {}
    client_name = data.get("client_name", "").strip()
    client_phone = data.get("client_phone", "").strip()
    date_str = data.get("date")

    if not client_name or not date_str:
        return jsonify({"error": "חייבים שם לקוח ותאריך"}), 400

    date_obj = datetime.fromisoformat(date_str).date()

    client = Client.query.filter_by(phone=client_phone).first()
    if not client:
        client = Client(full_name=client_name, phone=client_phone)
        db.session.add(client)
        db.session.flush()

    ev = Event(
        client_id=client.id,
        date=date_obj,
        type=data.get("type"),
        location=data.get("location"),
        celebrant=data.get("celebrant"),
        tz=data.get("tz"),
        status=data.get("status", "פתוח"),
        details=data.get("details"),
        categories=data.get("categories"),
        price=data.get("price"),
        deposit=data.get("deposit"),
        deposit_to=data.get("deposit_to"),
        expenses=data.get("expenses"),
    )
    db.session.add(ev)
    db.session.commit()

    return jsonify(event_to_dict(ev)), 201

@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    ev = Event.query.get_or_404(event_id)
    return jsonify(event_to_dict(ev))

@events_bp.route("/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    ev = Event.query.get_or_404(event_id)
    data = request.get_json() or {}

    if "date" in data and data["date"]:
        ev.date = datetime.fromisoformat(data["date"]).date()
    ev.type = data.get("type", ev.type)
    ev.location = data.get("location", ev.location)
    ev.celebrant = data.get("celebrant", ev.celebrant)
    ev.tz = data.get("tz", ev.tz)
    ev.status = data.get("status", ev.status)
    ev.details = data.get("details", ev.details)
    ev.categories = data.get("categories", ev.categories)
    ev.price = data.get("price", ev.price)
    ev.deposit = data.get("deposit", ev.deposit)
    ev.deposit_to = data.get("deposit_to", ev.deposit_to)
    ev.expenses = data.get("expenses", ev.expenses)

    db.session.commit()
    return jsonify(event_to_dict(ev))

@events_bp.route("/<int:event_id>/workers", methods=["POST"])
def add_event_worker(event_id):
    ev = Event.query.get_or_404(event_id)
    data = request.get_json() or {}
    w = EventWorker(
        event=ev,
        name=data.get("name", ""),
        category=data.get("category"),
        amount=data.get("amount"),
        note=data.get("note"),
    )
    db.session.add(w)
    db.session.commit()
    return jsonify({"ok": True, "worker_id": w.id})

@events_bp.route("/<int:event_id>/meetings", methods=["POST"])
def add_event_meeting(event_id):
    ev = Event.query.get_or_404(event_id)
    data = request.get_json() or {}
    m = EventMeeting(
        event=ev,
        type=data.get("type"),
        date=data.get("date"),
        time=data.get("time"),
        location=data.get("location"),
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"ok": True, "meeting_id": m.id})
