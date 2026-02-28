"""Unit tests for swimapi utility functions: require_auth, get_current_user, require_admin."""
import pytest
from werkzeug.exceptions import Forbidden
from swimapi.utils import get_current_user, require_admin, require_auth
from swimapi.models import db, User


class TestRequireAuth:
    """Tests for the require_auth() helper."""

    def test_missing_header(self, client):
        """require_auth() should raise Forbidden when the API key header is absent."""
        user = User(
            name="Test User",
            email="test@test.com",
            api_key="test-api-key",
            user_type="customer"
        )

        with client.application.test_request_context("/"):
            with pytest.raises(Forbidden) as exc:
                require_auth(user)

        assert "Missing swimapi-api-key header." in str(exc.value)

    def test_invalid_api_key(self, client):
        """require_auth() should raise Forbidden when the API key does not match."""
        user = User(
            name="Test User",
            email="test@test.com",
            api_key="correct-key",
            user_type="customer"
        )

        with client.application.test_request_context(
            "/", headers={"swimapi-api-key": "wrong-key"}
        ):
            with pytest.raises(Forbidden) as exc:
                require_auth(user)

        assert "Invalid API key." in str(exc.value)

    def test_valid_api_key(self, client):
        """require_auth() should not raise when the correct API key is provided."""
        user = User(
            name="Test User",
            email="test@test.com",
            api_key="correct-key",
            user_type="customer"
        )

        with client.application.test_request_context(
            "/", headers={"swimapi-api-key": "correct-key"}
        ):
            require_auth(user)


class TestGetCurrentUser:
    """Tests for the get_current_user() helper."""

    def test_missing_header(self, client):
        """get_current_user() should raise Forbidden when the API key header is absent."""
        with client.application.test_request_context("/"):
            with pytest.raises(Forbidden) as exc:
                get_current_user()

        assert "Missing swimapi-api-key header." in str(exc.value)

    def test_invalid_api_key(self, client):
        """get_current_user() should raise Forbidden when no user matches the key."""
        with client.application.test_request_context(
            "/", headers={"swimapi-api-key": "nonexistent-key"}
        ):
            with pytest.raises(Forbidden) as exc:
                get_current_user()

        assert "Invalid API key." in str(exc.value)

    def test_valid_api_key(self, client):
        """get_current_user() should return the matching User for a valid key."""
        user = User(
            name="Test User",
            email="test@test.com",
            api_key="correct-key",
            user_type="customer"
        )
        db.session.add(user)
        db.session.commit()

        with client.application.test_request_context(
            "/", headers={"swimapi-api-key": "correct-key"}
        ):
            current = get_current_user()

        assert current is not None
        assert isinstance(current, User)
        assert current.user_id == user.user_id
        assert current.email == "test@test.com"
        assert current.api_key == "correct-key"


class TestRequireAdmin:
    """Tests for the require_admin() helper."""

    def test_non_admin_user(self, client):
        """require_admin() should raise Forbidden for a non-admin user."""
        with client.application.app_context():
            user = User(
                name="Regular User",
                email="regular@test.com",
                api_key="regular-user-key",
                user_type="customer"
            )
            db.session.add(user)
            db.session.commit()

        with client.application.test_request_context(
            "/", headers={"swimapi-api-key": "regular-user-key"}
        ):
            with pytest.raises(Forbidden) as exc:
                require_admin()

        assert "Admin privileges required." in str(exc.value)

    def test_admin_user(self, client):
        """require_admin() should not raise for an admin user."""
        with client.application.app_context():
            user = User(
                name="Admin User",
                email="admin@test.com",
                api_key="admin-key",
                user_type="admin"
            )
            db.session.add(user)
            db.session.commit()

        with client.application.test_request_context(
            "/", headers={"swimapi-api-key": "admin-key"}
        ):
            require_admin()

        assert True
