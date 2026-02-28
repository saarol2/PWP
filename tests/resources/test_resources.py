"""Tests for the resource endpoints."""
import json

from swimapi.models import db, Resource


def _get_resource_json(name="Test Pool", resource_type="pool"):
    return {"name": name, "description": "A test resource", "resource_type": resource_type}


class TestResourceCollection:
    """Tests for the /api/resources collection endpoint."""
    RESOURCE_URL = "/api/resources"

    def test_get(self, client):
        """GET should return 200 and a list of resources."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_post_valid_request(self, client):
        """POST with valid JSON and admin key should return 201 and the new resource."""
        body = _get_resource_json(name="New Pool")
        resp = client.post(
            self.RESOURCE_URL, json=body, headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["name"] == body["name"]
        assert data["resource_type"] == body["resource_type"]

    def test_post_not_admin(self, client):
        """POST with a non-admin key should return 403."""
        resp = client.post(
            self.RESOURCE_URL,
            json=_get_resource_json(),
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 403

    def test_post_wrong_content_type(self, client):
        """POST with a non-JSON content type should return 415."""
        resp = client.post(
            self.RESOURCE_URL,
            data=json.dumps(_get_resource_json()),
            content_type="text/plain",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 415

    def test_post_missing_field(self, client):
        """POST without required field resource_type should return 400."""
        resp = client.post(
            self.RESOURCE_URL,
            json={"name": "No Type"},
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 400


class TestResourceItem:
    """Tests for the /api/resources/<id> item endpoint."""

    def test_get_valid(self, client):
        """GET with a valid ID should return 200 and the resource data."""
        with client.application.app_context():
            r = Resource.query.first()
            rid = r.resource_id
            name = r.name

        resp = client.get(f"/api/resources/{rid}")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["resource_id"] == rid
        assert body["name"] == name

    def test_get_missing(self, client):
        """GET for a nonexistent ID should return 404."""
        resp = client.get("/api/resources/999999")
        assert resp.status_code == 404

    def test_put_valid(self, client):
        """PUT with valid data and admin key should return 204 and update the resource."""
        with client.application.app_context():
            r = Resource.query.first()
            rid = r.resource_id

        updated = {"name": "Updated Pool", "resource_type": "pool"}
        resp = client.put(
            f"/api/resources/{rid}",
            json=updated,
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 204

        resp2 = client.get(f"/api/resources/{rid}")
        body2 = json.loads(resp2.data)
        assert body2["name"] == "Updated Pool"

    def test_put_not_admin(self, client):
        """PUT with a non-admin key should return 403."""
        with client.application.app_context():
            rid = Resource.query.first().resource_id

        resp = client.put(
            f"/api/resources/{rid}",
            json={"name": "X", "resource_type": "pool"},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 403

    def test_put_wrong_mediatype(self, client):
        """PUT with a non-JSON content type should return 415."""
        with client.application.app_context():
            rid = Resource.query.first().resource_id

        resp = client.put(
            f"/api/resources/{rid}",
            data="{}",
            content_type="text/plain",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 415

    def test_put_missing_field(self, client):
        """PUT without required field resource_type should return 400."""
        with client.application.app_context():
            rid = Resource.query.first().resource_id

        resp = client.put(
            f"/api/resources/{rid}",
            json={"name": "No Type"},
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 400

    def test_put_conflict(self, client):
        """PUT with a name that already exists should return 409."""
        with client.application.app_context():
            resources = Resource.query.limit(2).all()
            rid1 = resources[0].resource_id
            name2 = resources[1].name

        resp = client.put(
            f"/api/resources/{rid1}",
            json={"name": name2, "resource_type": "pool"},
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 409

    def test_delete_valid(self, client):
        """DELETE with admin key should return 204 and make the item unreachable."""
        with client.application.app_context():
            r = Resource(name="ToDelete", resource_type="gym")
            db.session.add(r)
            db.session.commit()
            rid = r.resource_id

        resp = client.delete(
            f"/api/resources/{rid}",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 204

        resp2 = client.get(f"/api/resources/{rid}")
        assert resp2.status_code == 404

    def test_delete_not_admin(self, client):
        """DELETE with a non-admin key should return 403."""
        with client.application.app_context():
            rid = Resource.query.first().resource_id

        resp = client.delete(
            f"/api/resources/{rid}",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 403

    def test_delete_missing(self, client):
        """DELETE for a nonexistent ID should return 404."""
        resp = client.delete(
            "/api/resources/999999",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 404
