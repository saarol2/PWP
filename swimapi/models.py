"""Database models for the swimapi application."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Represents a user of the swim facility."""

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    api_key = db.Column(db.String(64), unique=True)
    user_type = db.Column(
        db.Enum('customer', 'admin'),
        default='customer',
        server_default='customer',
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

    def serialize(self):
        """Return a dictionary representation of the user."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "user_type": self.user_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def deserialize(self, doc):
        """Populate the user's fields from a dictionary."""
        self.name = doc["name"]
        self.email = doc["email"]
        self.user_type = doc.get("user_type", "customer")

    @staticmethod
    def json_schema():
        """Return the JSON schema for validating user data."""
        schema = {
            "type": "object",
            "required": ["name", "email"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "User's full name",
            "type": "string"
        }
        props["email"] = {
            "description": "User's unique email address",
            "type": "string",
            "format": "email"
        }
        props["user_type"] = {
            "description": "Role of the user",
            "type": "string",
            "enum": ["customer", "admin"]
        }
        return schema

class Resource(db.Model):
    """Represents a bookable resource such as a pool, sauna, or gym."""

    resource_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(
        db.Enum('pool', 'sauna', 'gym'),
        nullable=False
    )

class Timeslot(db.Model):
    """Represents a time slot associated with a bookable resource."""

    slot_id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(
        db.Integer,
        db.ForeignKey('resource.resource_id', ondelete='CASCADE'),
        nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    resource = db.relationship('Resource', backref=db.backref('timeslots', lazy=True))

class Reservation(db.Model):
    """Represents a reservation made by a user for a time slot."""

    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=False
    )
    slot_id = db.Column(
        db.Integer,
        db.ForeignKey('timeslot.slot_id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    status = db.Column(
        db.Enum('pending', 'confirmed', 'cancelled', 'completed'),
        default='pending',
        server_default='pending',
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

    user = db.relationship('User', backref=db.backref('reservations', lazy=True))
    timeslot = db.relationship('Timeslot', backref=db.backref('reservations', lazy=True))
