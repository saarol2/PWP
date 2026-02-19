"""Flask application factory for the swimapi package."""

from flask import Flask
from .models import db


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
