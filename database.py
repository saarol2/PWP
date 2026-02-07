from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)


"""Database models for the reservation system"""

"""User table"""
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    user_type = db.Column(db.Enum('customer', 'admin'), default='customer', server_default='customer', nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
    
"""Resource table"""    
class Resource(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(db.Enum('pool', 'sauna', 'gym'), nullable=False)

    def __repr__(self):
        return f'<Resource {self.name}>'

"""Timeslot table"""
class Timeslot(db.Model):
    slot_id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.resource_id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    resource = db.relationship('Resource', backref=db.backref('timeslots', lazy=True))

    def __repr__(self):
        return f'<Timeslot {self.start_time} - {self.end_time}>'
    
"""Reservation table"""
class Reservation(db.Model):
    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('timeslot.slot_id', ondelete='CASCADE'), nullable=False, unique=True)
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'completed'), default='pending', server_default='pending', nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    user = db.relationship('User', backref=db.backref('reservations', lazy=True))
    timeslot = db.relationship('Timeslot', backref=db.backref('reservations', lazy=True))

    def __repr__(self):
        return f'<Reservation User {self.user_id} Slot {self.slot_id}>'
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created.")
