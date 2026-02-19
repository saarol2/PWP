"""Database models for the swimapi application."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Represents a user of the swim facility."""

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
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
