from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # שדות תפקיד/מצב
    role = db.Column(db.String(50), nullable=False, default="user")
    full_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")

    # שדות תשלום/תפקיד באירוע (לא חובה לשימוש מידי)
    event_role = db.Column(db.String(50))
    payment_type = db.Column(db.String(50))
    payment_amount = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "phone": self.phone,
            "status": self.status,
            "event_role": self.event_role,
            "payment_type": self.payment_type,
            "payment_amount": self.payment_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))

    event_type = db.Column(db.String(100))   # סוג אירוע (חתונה/בר מצווה וכו')
    source = db.Column(db.String(100))       # מאיפה הגיע הלקוח (פייסבוק, אינסטה...)
    status = db.Column(db.String(50), default="new")
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # קשר לאירועים
    events = db.relationship("Event", backref="client", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "event_type": self.event_type,
            "source": self.source,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # שם האירוע
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)

    event_type = db.Column(db.String(100))             # חתונה / בר מצווה וכו'
    location = db.Column(db.String(255))
    status = db.Column(db.String(50), default="planning")
    budget = db.Column(db.Float)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time.isoformat() if self.time else None,
            "event_type": self.event_type,
            "location": self.location,
            "status": self.status,
            "budget": self.budget,
            "client_id": self.client_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))

    source = db.Column(db.String(100))                 # מקור ליד
    status = db.Column(db.String(50), default="new")
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "source": self.source,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
