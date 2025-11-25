from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), nullable=False, default="user")
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
