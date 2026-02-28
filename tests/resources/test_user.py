import pytest
import json

from swimapi.models import db, User

def _get_user_json(name="Extra User", email="extra@example.com"):
    return {"name": name, "email": email, "user_type": "customer"}

class TestUserCollection(object):
    RESOURCE_URL = "/api/users"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
    
    def test_post_valid_request(self, client):
        user_json = _get_user_json()
        resp = client.post(self.RESOURCE_URL, json=user_json)
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["name"] == user_json["name"]
        assert data["email"] == user_json["email"]
        assert data["user_type"] == user_json["user_type"]
    
    def test_post_wrong_content_type(self, client):
        valid = _get_user_json()
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
    
    def test_post_missing_field(self, client):
        valid = _get_user_json()
        valid.pop("email")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
    
    def test_post_conflict_email_exists(self, client):
        valid = _get_user_json(name="First", email="dup@example.com")
        client.post(self.RESOURCE_URL, json=valid)
        dup = _get_user_json(name="Second", email="dup@example.com")
        resp = client.post(self.RESOURCE_URL, json=dup)
        assert resp.status_code == 409
    

class TestUserItem(object):

    def test_get_valid(self, client):
        with client.application.app_context():
            u = User.query.filter_by(email="alice@example.com").first()
            uid = u.user_id

        resp = client.get(f"/api/users/{uid}")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["email"] == "alice@example.com"
    
    def test_get_missing(self, client):
        resp = client.get("/api/users/999999")
        assert resp.status_code == 404
    
    def test_put_valid(self, client):
        with client.application.app_context():
            u = User.query.filter_by(email="alice@example.com").first()
            uid = u.user_id

        updated = {"name": "Alice Updated", "email": "alice.updated@example.com", "user_type": "customer"}
        resp = client.put(
            f"/api/users/{uid}",
            json=updated,
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 204

        resp2 = client.get(f"/api/users/{uid}")
        assert resp2.status_code == 200
        body2 = json.loads(resp2.data)
        assert body2["name"] == "Alice Updated"

    def test_put_wrong_key(self, client):
        with client.application.app_context():
            u = User.query.filter_by(email="alice@example.com").first()
            uid = u.user_id

        updated = {"name": "X", "email": "alice@example.com", "user_type": "customer"}
        resp = client.put(
            f"/api/users/{uid}",
            json=updated,
            headers={"swimapi-api-key": "wrong-key"}
        )
        assert resp.status_code == 403

    def test_put_wrong_mediatype(self, client):
        with client.application.app_context():
            u = User.query.filter_by(email= "alice@example.com").first()
            uid = u.user_id

        updated = {"name": "X", "email": "alice@example.com", "user_type": "customer"}
        resp = client.put(
            f"/api/users/{uid}",
            data=json.dumps(updated),
            content_type="text/plain",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 415

    def test_put_missing_field(self, client):
        with client.application.app_context():
            u = User.query.filter_by(email="alice@example.com").first()
            uid = u.user_id

        resp = client.put(
            f"/api/users/{uid}",
            json={"name": "No Email"},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 400

    def test_put_conflict_email(self, client):
        with client.application.app_context():
            alice = User.query.filter_by(email="alice@example.com").first()
            uid = alice.user_id

        resp = client.put(
            f"/api/users/{uid}",
            json={"name": "Alice", "email": "bob@example.com", "user_type": "customer"},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 409

    def test_delete_valid(self, client):
        with client.application.app_context():
            u = User(name="ToDelete", email="todelete@example.com", api_key="del-key", user_type="customer")
            db.session.add(u)
            db.session.commit()
            uid = u.user_id

        resp = client.delete(
            f"/api/users/{uid}",
            headers={"swimapi-api-key": "del-key"}
        )
        assert resp.status_code == 204

        resp2 = client.get(f"/api/users/{uid}")
        assert resp2.status_code == 404

    def test_delete_wrong_key(self, client):
        with client.application.app_context():
            u = User.query.filter_by(email="alice@example.com").first()
            uid = u.user_id

        resp = client.delete(
            f"/api/users/{uid}",
            headers={"swimapi-api-key": "wrong-key"}
        )
        assert resp.status_code == 403

    def test_delete_missing(self, client):
        resp = client.delete(
            "/api/users/999999",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 404

class TestAdminUserCollection(object):
    RESOURCE_URL = "/api/admin/users"

    def test_post_valid_request_creates_admin(self, client):
        valid = {"name": "Admin X", "email": "adminx@example.com", "user_type": "customer"}
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201

        body = json.loads(resp.data)
        assert body["email"] == "adminx@example.com"
        assert body["user_type"] == "admin"
        assert "api_key" in body

        with client.application.app_context():
            u = User.query.filter_by(email="adminx@example.com").first()
            assert u is not None
            assert u.user_type == "admin"

    def test_post_wrong_mediatype(self, client):
        valid = {"name": "Admin Y", "email": "adminy@example.com", "user_type": "customer"}
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

    def test_post_missing_field(self, client):
        valid = {"name": "Admin Z", "user_type": "customer"}
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

    def test_post_conflict_email_exists(self, client):
        first = {"name": "AdminFirst", "email": "dup-admin@example.com", "user_type": "admin"}
        client.post(self.RESOURCE_URL, json=first)
        dup = {"name": "AdminSecond", "email": "dup-admin@example.com", "user_type": "admin"}
        resp = client.post(self.RESOURCE_URL, json=dup)
        assert resp.status_code == 409
