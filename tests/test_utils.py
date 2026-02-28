import pytest
from werkzeug.exceptions import Forbidden
from swimapi.utils import get_current_user, require_admin, require_auth
from swimapi.models import db, User


class TestRequireAuth:

    def test_missing_header(self, client):
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

    def test_missing_header(self, client):
        with client.application.test_request_context("/"):
            with pytest.raises(Forbidden) as exc:
                get_current_user()

        assert "Missing swimapi-api-key header." in str(exc.value)

    def test_invalid_api_key(self, client):
        with client.application.test_request_context(
            "/", headers={"swimapi-api-key": "nonexistent-key"}
        ):
            with pytest.raises(Forbidden) as exc:
                get_current_user()

        assert "Invalid API key." in str(exc.value)

    def test_valid_api_key(self, client):
        user = User(
            name="Test User",
            email="test@test.com",
            api_key="correct-key",
            user_type="customer"
        )
        db.session.add(user)
        db.session.commit()

        with client.application.test_request_context("/", headers={"swimapi-api-key": "correct-key"}):
            current = get_current_user()

        assert current is not None
        assert isinstance(current, User)
        assert current.user_id == user.user_id
        assert current.email == "test@test.com"
        assert current.api_key == "correct-key"

class TestRequireAdmin:

    def test_non_admin_user(self, client):
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
