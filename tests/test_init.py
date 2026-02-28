"""Tests for swimapi/__init__.py (application factory)."""

import pytest
from flask import Flask
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from swimapi import create_app
from swimapi.models import db, User, Reservation


def _populate_db():
    """Optional: Insert minimal data used by some API tests."""
    u = User(name="Seed User", email="seed@example.com", api_key="seedkey", user_type="customer")
    db.session.add(u)
    db.session.commit()


@pytest.fixture
def client():
    """Yield a Flask test client with a fresh in-memory DB (course style)."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    ctx = app.app_context()
    ctx.push()

    db.drop_all()
    db.create_all()

    yield app.test_client()

    db.session.rollback()
    db.drop_all()
    db.session.remove()
    ctx.pop()


class TestCreateApp(object):

    def test_returns_flask_instance(self):
        application = create_app()
        assert isinstance(application, Flask)

    def test_has_sqlalchemy_uri(self):
        application = create_app()
        assert "SQLALCHEMY_DATABASE_URI" in application.config
        assert application.config["SQLALCHEMY_DATABASE_URI"]

    def test_track_modifications_disabled(self):
        application = create_app()
        assert application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False

    def test_creates_different_instances(self):
        app1 = create_app()
        app2 = create_app()
        assert app1 is not app2

    def test_debug_mode_off_by_default(self):
        application = create_app()
        assert application.debug is False


class TestDatabaseInit(object):

    def test_tables_created(self, client):
        app = client.application
        with app.app_context():
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()

        assert "user" in table_names
        assert "resource" in table_names
        assert "timeslot" in table_names
        assert "reservation" in table_names

    def test_can_insert_and_query_user(self, client):
        app = client.application
        with app.app_context():
            user = User(
                name="Test User",
                email="test@example.com",
                api_key="testkey",
                user_type="customer",
            )
            db.session.add(user)
            db.session.commit()

            fetched = User.query.filter_by(email="test@example.com").first()
            assert fetched is not None
            assert fetched.name == "Test User"

    def test_foreign_key_constraint_enforced(self, client):
        """Inserting a Reservation with a nonexistent slot_id must fail (FK ON)."""
        app = client.application
        with app.app_context():
            user = User(
                name="FK User",
                email="fk@example.com",
                api_key="fkkey",
                user_type="customer",
            )
            db.session.add(user)
            db.session.commit()

            bad_reservation = Reservation(user_id=user.user_id, slot_id=99999)
            db.session.add(bad_reservation)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()


class TestSQLitePragma(object):

    def test_foreign_keys_pragma_on(self, client):
        app = client.application
        with app.app_context():
            result = db.session.execute(db.text("PRAGMA foreign_keys")).scalar()
        assert result == 1


class TestRoutesRegistered(object):

    def test_has_registered_routes(self, client):
        app = client.application
        rules = [r.rule for r in app.url_map.iter_rules() if r.endpoint != "static"]
        assert len(rules) > 0

    def test_api_users_endpoint_reachable(self, client):
        resp = client.get("/api/users")
        assert resp.status_code != 404

    def test_api_resources_endpoint_reachable(self, client):
        resp = client.get("/api/resources")
        assert resp.status_code != 404
