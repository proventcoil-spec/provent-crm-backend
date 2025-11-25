from datetime import datetime
from extensions import db

# ==========================
# USER MODEL
# ==========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), default="user", nullable=False)
    full_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")

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
            "created_at": self.created_at.isoformat(),
        }


# ==========================
# CLIENT MODEL
# ==========================
class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    event_type = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "event_type": self.event_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


# ==========================
# LEAD MODEL
# ==========================
class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    source = db.Column(db.String(255))
    status = db.Column(db.String(255), default="new")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "source": self.source,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


# ==========================
# EVENT MODEL
# ==========================
class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.String(50))
    event_type = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "event_date": self.event_date,
            "event_type": self.event_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


# ==========================
# MEDIA FILE MODEL
# ==========================
class MediaFile(db.Model):
    __tablename__ = "media_files"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    event = db.relationship("Event", backref=db.backref("media_files", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "url": self.url,
            "uploaded_at": self.uploaded_at.isoformat(),
            "event_id": self.event_id,
        }
