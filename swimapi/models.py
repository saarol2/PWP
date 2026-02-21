"""Database models for the swimapi application."""

from datetime import datetime
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

    def serialize(self):
        """Return a dictionary representation of the resource."""
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type,
        }

    def deserialize(self, doc):
        """Populate the resource's fields from a dictionary."""
        self.name = doc["name"]
        self.description = doc.get("description")
        self.resource_type = doc["resource_type"]

    @staticmethod
    def json_schema():
        """Return the JSON schema for validating resource data."""
        schema = {
            "type": "object",
            "required": ["name", "resource_type"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of the resource",
            "type": "string"
        }
        props["description"] = {
            "description": "Optional description of the resource",
            "type": "string"
        }
        props["resource_type"] = {
            "description": "Type of the resource",
            "type": "string",
            "enum": ["pool", "sauna", "gym"]
        }
        return schema

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

    resource = db.relationship(
        'Resource',
        backref=db.backref('timeslots', lazy=True, passive_deletes=True)
        )

    def serialize(self):
        """Return a dictionary representation of the timeslot."""
        return {
            "slot_id": self.slot_id,
            "resource_id": self.resource_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "reservation": self.reservations[0].serialize() if self.reservations else None,
        }

    def deserialize(self, doc):
        """Populate the timeslot's fields from a dictionary."""
        self.resource_id = doc["resource_id"]
        self.start_time = datetime.fromisoformat(doc["start_time"])
        self.end_time = datetime.fromisoformat(doc["end_time"])

    @staticmethod
    def json_schema():
        """Return the JSON schema for validating timeslot data."""
        schema = {
            "type": "object",
            "required": ["resource_id", "start_time", "end_time"]
        }
        props = schema["properties"] = {}
        props["resource_id"] = {
            "description": "ID of the associated resource",
            "type": "integer"
        }
        props["start_time"] = {
            "description": "Start time in ISO 8601 format",
            "type": "string",
            "format": "date-time"
        }
        props["end_time"] = {
            "description": "End time in ISO 8601 format",
            "type": "string",
            "format": "date-time"
        }
        return schema

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
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

    user = db.relationship(
        'User',
        backref=db.backref('reservations', lazy=True, passive_deletes=True)
        )
    timeslot = db.relationship(
        'Timeslot',
        backref=db.backref('reservations', lazy=True, passive_deletes=True)
        )

    def serialize(self):
        """Return a dictionary representation of the reservation."""
        return {
            "reservation_id": self.reservation_id,
            "user_id": self.user_id,
            "slot_id": self.slot_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def deserialize(self, doc):
        """Populate the reservation's fields from a dictionary."""
        self.user_id = doc["user_id"]
        self.slot_id = doc["slot_id"]

    @staticmethod
    def json_schema():
        """Return the JSON schema for validating reservation data."""
        schema = {
            "type": "object",
            "required": ["user_id", "slot_id"]
        }
        props = schema["properties"] = {}
        props["user_id"] = {
            "description": "ID of the user making the reservation",
            "type": "integer"
        }
        props["slot_id"] = {
            "description": "ID of the timeslot to reserve",
            "type": "integer"
        }
        return schema

    @staticmethod
    def post_schema():
        """Return the JSON schema for POST requests."""
        schema = {
            "type": "object",
            "required": ["slot_id"]
        }
        props = schema["properties"] = {}
        props["slot_id"] = {
            "description": "ID of the timeslot to reserve",
            "type": "integer"
        }
        return schema
