from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(db.Model, UserMixin):
    """
    A single table holds both clients and admins, distinguished by `role`.
    UserMixin supplies the is_authenticated / is_active / get_id() methods
    Flask-Login needs to manage the session.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('full_name',db.String(120), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("client", "admin", name="user_role"), nullable=False, default="client")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship(
        "Appointment", backref="client", lazy=True, cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", backref="author", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(190), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, default=0)
    price_per_event = db.Column(db.Numeric(10, 2), default=0)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship(
        "Appointment", backref="venue", lazy=True, cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", backref="venue", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "description": self.description,
            "capacity": self.capacity,
            "price_per_event": float(self.price_per_event),
            "image_url": self.image_url,
        }


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    guest_count = db.Column(db.Integer)
    notes = db.Column(db.Text)
    status = db.Column(
        db.Enum("pending", "confirmed", "rejected", name="appointment_status"),
        default="pending",
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment user={self.user_id} venue={self.venue_id} status={self.status}>"


class Review(db.Model):
    """
    A client's review of a venue. Only clients with a *confirmed*
    appointment at that venue are allowed to leave one (enforced in
    the /venues/<id>/reviews route) — this keeps the feature tied to
    a genuine booking rather than open to anyone.
    """

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Review user={self.user_id} venue={self.venue_id} rating={self.rating}>"
