"""Tests for the timeslot endpoints."""
import json
from datetime import datetime

from swimapi.models import Resource, db, Timeslot


class TestTimeslotCollection:
    """Tests for the /api/timeslots collection endpoint."""
    RESOURCE_URL = "/api/timeslots"

    def test_get(self, client):
        """GET should return 200 and a list of timeslots."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_post_valid_request(self, client):
        """POST with valid JSON and admin key should return 201 and the new timeslot."""
        with client.application.app_context():
            resource_id = Resource.query.first().resource_id

        timeslot_json = {
            "resource_id": resource_id,
            "start_time": datetime(2024, 7, 1, 10, 0).isoformat() + "Z",
            "end_time": datetime(2024, 7, 1, 11, 0).isoformat() + "Z"
        }
        resp = client.post(
            self.RESOURCE_URL,
            json=timeslot_json,
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["resource_id"] == resource_id

    def test_post_wrong_content_type(self, client):
        """POST with a non-JSON content type should return 415."""
        valid = {
            "start_time": datetime(2024, 7, 1, 10, 0).isoformat() + "Z",
            "end_time": datetime(2024, 7, 1, 11, 0).isoformat() + "Z"
        }
        resp = client.post(
            self.RESOURCE_URL,
            data=json.dumps(valid),
            content_type="text/plain",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 415

    def test_post_missing_field(self, client):
        """POST without required fields should return 400."""
        valid = {
            "start_time": datetime(2024, 7, 1, 10, 0).isoformat() + "Z"
        }
        resp = client.post(
            self.RESOURCE_URL,
            json=valid,
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 400

    def test_post_conflict(self, client):
        """POSTing the same timeslot twice should return 409 on the second request."""
        with client.application.app_context():
            resource_id = Resource.query.first().resource_id

        slot = {
            "resource_id": resource_id,
            "start_time": datetime(2024, 8, 1, 10, 0).isoformat() + "Z",
            "end_time": datetime(2024, 8, 1, 11, 0).isoformat() + "Z"
        }
        client.post(self.RESOURCE_URL, json=slot, headers={"swimapi-api-key": "admin-api-key"})
        resp = client.post(
            self.RESOURCE_URL, json=slot, headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 409


class TestTimeslotItem:
    """Tests for the /api/timeslots/<id> item endpoint."""

    def test_get_valid(self, client):
        """GET with a valid ID should return 200 and the timeslot data."""
        with client.application.app_context():
            ts = Timeslot.query.first()
            sid = ts.slot_id
            resource_id = ts.resource_id

        resp = client.get(f"/api/timeslots/{sid}")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["slot_id"] == sid
        assert body["resource_id"] == resource_id

    def test_get_missing(self, client):
        """GET for a nonexistent ID should return 404."""
        resp = client.get("/api/timeslots/999999")
        assert resp.status_code == 404

    def test_put_valid(self, client):
        """PUT with valid data and admin key should return 204 and update the timeslot."""
        with client.application.app_context():
            ts = Timeslot.query.first()
            sid = ts.slot_id
            resource_id = ts.resource_id

        updated = {
            "resource_id": resource_id,
            "start_time": datetime(2025, 1, 1, 8, 0).isoformat() + "Z",
            "end_time": datetime(2025, 1, 1, 9, 0).isoformat() + "Z"
        }
        resp = client.put(
            f"/api/timeslots/{sid}",
            json=updated,
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 204

        resp2 = client.get(f"/api/timeslots/{sid}")
        assert resp2.status_code == 200
        body2 = json.loads(resp2.data)
        assert body2["resource_id"] == resource_id

    def test_put_not_admin(self, client):
        """PUT with a non-admin key should return 403."""
        with client.application.app_context():
            ts = Timeslot.query.first()
            sid = ts.slot_id
            resource_id = ts.resource_id

        updated = {
            "resource_id": resource_id,
            "start_time": datetime(2025, 1, 1, 8, 0).isoformat() + "Z",
            "end_time": datetime(2025, 1, 1, 9, 0).isoformat() + "Z"
        }
        resp = client.put(
            f"/api/timeslots/{sid}",
            json=updated,
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 403

    def test_put_wrong_mediatype(self, client):
        """PUT with a non-JSON content type should return 415."""
        with client.application.app_context():
            sid = Timeslot.query.first().slot_id

        resp = client.put(
            f"/api/timeslots/{sid}",
            data="{}",
            content_type="text/plain",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 415

    def test_put_missing_field(self, client):
        """PUT without required fields should return 400."""
        with client.application.app_context():
            sid = Timeslot.query.first().slot_id

        resp = client.put(
            f"/api/timeslots/{sid}",
            json={"start_time": datetime(2025, 1, 1, 8, 0).isoformat() + "Z"},
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 400

    def test_put_conflict(self, client):
        """PUT using times of another slot should return 409."""
        with client.application.app_context():
            slots = Timeslot.query.limit(2).all()
            sid1 = slots[0].slot_id
            resource_id = slots[1].resource_id
            start_time = slots[1].start_time.isoformat() + "Z"
            end_time = slots[1].end_time.isoformat() + "Z"

        resp = client.put(
            f"/api/timeslots/{sid1}",
            json={"resource_id": resource_id, "start_time": start_time, "end_time": end_time},
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 409

    def test_delete_valid(self, client):
        """DELETE with admin key should return 204 and make the slot unreachable."""
        with client.application.app_context():
            ts = Timeslot(
                resource_id=Resource.query.first().resource_id,
                start_time=datetime(2030, 1, 1, 8, 0),
                end_time=datetime(2030, 1, 1, 9, 0)
            )
            db.session.add(ts)
            db.session.commit()
            sid = ts.slot_id

        resp = client.delete(
            f"/api/timeslots/{sid}",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 204

        resp2 = client.get(f"/api/timeslots/{sid}")
        assert resp2.status_code == 404

    def test_delete_not_admin(self, client):
        """DELETE with a non-admin key should return 403."""
        with client.application.app_context():
            sid = Timeslot.query.first().slot_id

        resp = client.delete(
            f"/api/timeslots/{sid}",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 403

    def test_delete_missing(self, client):
        """DELETE for a nonexistent ID should return 404."""
        resp = client.delete(
            "/api/timeslots/999999",
            headers={"swimapi-api-key": "admin-api-key"}
        )
        assert resp.status_code == 404
