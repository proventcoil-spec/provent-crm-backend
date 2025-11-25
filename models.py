
from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50))
    type = db.Column(db.String(50))
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_role = db.Column(db.String(50))
    payment_type = db.Column(db.String(50))
    payment_amount = db.Column(db.Numeric(10, 2))


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100))
    full_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    event_type = db.Column(db.String(100))
    event_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default="חדש")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    city = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))
    date = db.Column(db.Date)
    location = db.Column(db.String(255))
    guests_count = db.Column(db.Integer)
    status = db.Column(db.String(50), default="פתוח")
    budget = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship("Client", backref=db.backref("events", lazy=True))


class MediaFile(db.Model):
    __tablename__ = "media_files"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    file_type = db.Column(db.String(20))
    path = db.Column(db.String(512), nullable=False)
    label = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship("Event", backref=db.backref("media_files", lazy=True))


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    pdf_path = db.Column(db.String(512))
    signed = db.Column(db.Boolean, default=False)
    signed_at = db.Column(db.DateTime)
    signed_ip = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship("Event", backref=db.backref("contracts", lazy=True))
    client = db.relationship("Client", backref=db.backref("contracts", lazy=True))
