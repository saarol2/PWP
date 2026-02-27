"""Tests for swimapi/__init__.py (application factory)."""

import pytest
from flask import Flask
from swimapi import create_app
from swimapi.models import db, User, Resource, Timeslot, Reservation

@pytest.fixture
def app():
    """Return a freshly created app configured for testing (in-memory DB)."""
    application = create_app()
    application.config["TESTING"] = True
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with application.app_context():
        db.drop_all()
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def app_client(app):
    return app.test_client()

class TestCreateApp:
    def test_returns_flask_instance(self):
        """create_app() must return a Flask application object."""
        application = create_app()
        assert isinstance(application, Flask)

    def test_has_sqlalchemy_uri(self):
        """The app must have a SQLALCHEMY_DATABASE_URI set."""
        application = create_app()
        assert "SQLALCHEMY_DATABASE_URI" in application.config
        assert application.config["SQLALCHEMY_DATABASE_URI"]

    def test_track_modifications_disabled(self):
        """SQLALCHEMY_TRACK_MODIFICATIONS should be False to suppress warnings."""
        application = create_app()
        assert application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False

    def test_creates_different_instances(self):
        """Each call to create_app() must produce an independent Flask instance."""
        app1 = create_app()
        app2 = create_app()
        assert app1 is not app2

    def test_debug_mode_off_by_default(self):
        """Debug mode must be off in the default factory output."""
        application = create_app()
        assert application.debug is False

class TestDatabaseInit:
    def test_tables_created(self, app):
        """All model tables must exist after create_app()."""
        with app.app_context():
            inspector = db.inspect(db.engine)
            table_names = inspector.get_table_names()
        assert "user" in table_names
        assert "resource" in table_names
        assert "timeslot" in table_names
        assert "reservation" in table_names

    def test_can_insert_and_query_user(self, app):
        """A User row inserted inside the app context must be readable."""
        with app.app_context():
            user = User(name="Test User", email="test@example.com",
                        api_key="testkey", user_type="customer")
            db.session.add(user)
            db.session.commit()
            fetched = User.query.filter_by(email="test@example.com").first()
            assert fetched is not None
            assert fetched.name == "Test User"

    def test_foreign_key_constraint_enforced(self, app):
        """Inserting a Reservation with a nonexistent slot_id must fail (FK ON)."""
        from sqlalchemy.exc import IntegrityError
        with app.app_context():
            user = User(name="FK User", email="fk@example.com",
                        api_key="fkkey", user_type="customer")
            db.session.add(user)
            db.session.commit()

            bad_reservation = Reservation(user_id=user.user_id, slot_id=99999)
            db.session.add(bad_reservation)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

class TestSQLitePragma:
    def test_foreign_keys_pragma_on(self, app):
        """PRAGMA foreign_keys must be ON for every new connection."""
        with app.app_context():
            result = db.session.execute(
                db.text("PRAGMA foreign_keys")
            ).scalar()
        assert result == 1

class TestRoutesRegistered:
    def test_has_registered_routes(self, app):
        """The application must expose at least one URL rule beyond the static route."""
        rules = [r.rule for r in app.url_map.iter_rules()
                 if r.endpoint != "static"]
        assert len(rules) > 0

    def test_api_users_endpoint_reachable(self, app_client):
        """A GET to /api/users must not return 404."""
        response = app_client.get("/api/users")
        assert response.status_code != 404

    def test_api_resources_endpoint_reachable(self, app_client):
        """A GET to /api/resources must not return 404."""
        response = app_client.get("/api/resources")
        assert response.status_code != 404
