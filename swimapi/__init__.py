"""Flask application factory for the swimapi package."""
import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flasgger import Swagger

from .models import db
from .extensions import cache
from .api import init_api


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    """Enable foreign key constraints for SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        if Path("/data").exists():
            db_file = Path("/data/example.db")
        else:
            Path(app.instance_path).mkdir(parents=True, exist_ok=True)
            db_file = Path(app.instance_path) / "example.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file.as_posix()}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SWAGGER"] = {
    "title": "SwimAPI",
    "openapi": "3.0.4",
    "uiversion": 3,
    "doc_dir": "./doc"
    }

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}},
        allow_headers=["Content-Type", "swimapi-api-key"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    swagger = Swagger(app, template_file="doc/base.yml")

    db.init_app(app)
    cache.init_app(app, config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 60})

    init_api(app)

    with app.app_context():
        db.create_all()

    return app
