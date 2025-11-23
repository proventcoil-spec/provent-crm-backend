from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ========== USERS (עובדים / ספקים) ==========
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), default="employee")  # employee / supplier
    system_role = db.Column(db.String(20), default="worker")  # owner/admin/team_lead/worker/supplier_only
    event_role = db.Column(db.String(120))
    status = db.Column(db.String(20), default="active")
    payment_type = db.Column(db.String(20))
    payment_amount = db.Column(db.String(50))
    internal_notes = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship("EventWorker", back_populates="worker")

# ========== CLIENTS ==========
class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship("Event", back_populates="client")

# ========== EVENTS ==========
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(120))
    location = db.Column(db.String(200))
    celebrant = db.Column(db.String(200))
    tz = db.Column(db.String(50))
    status = db.Column(db.String(20), default="פתוח")  # פתוח / בתהליך / סגור / בוטל
    details = db.Column(db.Text)
    categories = db.Column(db.Text)
    price = db.Column(db.Integer)
    deposit = db.Column(db.Integer)
    deposit_to = db.Column(db.String(20))  # shlomi / shimon / other
    expenses = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship("Client", back_populates="events")
    workers = db.relationship("EventWorker", back_populates="event", cascade="all, delete-orphan")
    meetings = db.relationship("EventMeeting", back_populates="event", cascade="all, delete-orphan")

class EventWorker(db.Model):
    __tablename__ = "event_workers"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(120))
    amount = db.Column(db.String(50))
    note = db.Column(db.Text)

    event = db.relationship("Event", back_populates="workers")
    worker = db.relationship("User", back_populates="events")

class EventMeeting(db.Model):
    __tablename__ = "event_meetings"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    type = db.Column(db.String(120))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    location = db.Column(db.String(200))

    event = db.relationship("Event", back_populates="meetings")

# ========== BUSINESS SETTINGS ==========
class BusinessSettings(db.Model):
    __tablename__ = "business_settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    legal_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    whatsapp = db.Column(db.String(200))
    address = db.Column(db.String(200))
    city = db.Column(db.String(120))
    website = db.Column(db.String(200))
    logo_url = db.Column(db.String(300))
    sms_sender = db.Column(db.String(50))

# ========== CONTRACT TEMPLATES ==========
class ContractTemplate(db.Model):
    __tablename__ = "contract_templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # event / supplier / client / other
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ========== CATEGORIES ==========
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # event_service / worker_role / lead_source / other

# ========== LEADS ==========
class Lead(db.Model):
    __tablename__ = "leads"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    source = db.Column(db.String(120))  # instagram / facebook / site / whatsapp / other
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default="חדש")  # חדש / בטיפול / סגור / לא רלוונטי
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========== PASSWORD CHANGES LOG ==========
class PasswordChange(db.Model):
    __tablename__ = "password_changes"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))  # user / client
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    client_name = db.Column(db.String(200))
    client_phone = db.Column(db.String(50))
    new_password = db.Column(db.String(200))
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
