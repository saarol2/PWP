"""Tests for the reservation resource."""
import json

from swimapi.models import Timeslot, Reservation


def _free_slot_id(client):
    """Return the slot_id of a timeslot that has no reservation."""
    with client.application.app_context():
        reserved_ids = {r.slot_id for r in Reservation.query.all()}
        slot = Timeslot.query.filter(
            ~Timeslot.slot_id.in_(reserved_ids)
        ).first()
        return slot.slot_id


class TestReservationCollection:
    """Tests for the /api/reservations collection endpoint."""
    RESOURCE_URL = "/api/reservations"

    def test_get_as_admin(self, client):
        """GET with admin key should return 200 and a list."""
        resp = client.get(self.RESOURCE_URL, headers={"swimapi-api-key": "admin-api-key"})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_get_not_admin(self, client):
        """GET with a non-admin key should return 403."""
        resp = client.get(self.RESOURCE_URL, headers={"swimapi-api-key": "customer-api-key1"})
        assert resp.status_code == 403

    def test_post_valid(self, client):
        """POST with a valid slot_id should return 201 and the new reservation."""
        slot_id = _free_slot_id(client)
        resp = client.post(
            self.RESOURCE_URL,
            json={"slot_id": slot_id},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["slot_id"] == slot_id

    def test_post_wrong_content_type(self, client):
        """POST with non-JSON content type should return 415."""
        resp = client.post(
            self.RESOURCE_URL,
            data='{"slot_id": 1}',
            content_type="text/plain",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 415

    def test_post_no_api_key(self, client):
        """POST without an API key should return 403."""
        slot_id = _free_slot_id(client)
        resp = client.post(self.RESOURCE_URL, json={"slot_id": slot_id})
        assert resp.status_code == 403

    def test_post_missing_field(self, client):
        """POST with an empty body should return 400."""
        resp = client.post(
            self.RESOURCE_URL,
            json={},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 400

    def test_post_conflict(self, client):
        """POSTing the same slot twice should return 409 on the second request."""
        slot_id = _free_slot_id(client)
        client.post(
            self.RESOURCE_URL,
            json={"slot_id": slot_id},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        resp = client.post(
            self.RESOURCE_URL,
            json={"slot_id": slot_id},
            headers={"swimapi-api-key": "customer-api-key2"}
        )
        assert resp.status_code == 409


class TestReservationItem:
    """Tests for the /api/reservations/<id> item endpoint."""

    def test_get_valid(self, client):
        """GET with the owner's key should return 200 and the reservation."""
        slot_id = _free_slot_id(client)
        post_resp = client.post(
            "/api/reservations",
            json={"slot_id": slot_id},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        rid = json.loads(post_resp.data)["reservation_id"]

        resp = client.get(
            f"/api/reservations/{rid}",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["reservation_id"] == rid

    def test_get_wrong_key(self, client):
        """GET with a different user's key should return 403."""
        slot_id = _free_slot_id(client)
        post_resp = client.post(
            "/api/reservations",
            json={"slot_id": slot_id},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        rid = json.loads(post_resp.data)["reservation_id"]

        resp = client.get(
            f"/api/reservations/{rid}",
            headers={"swimapi-api-key": "customer-api-key2"}
        )
        assert resp.status_code == 403

    def test_get_missing(self, client):
        """GET for a nonexistent reservation ID should return 404."""
        resp = client.get(
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 404

    def test_delete_valid(self, client):
        """DELETE with the owner's key should return 204 and make the item unreachable."""
        slot_id = _free_slot_id(client)
        post_resp = client.post(
            "/api/reservations",
            json={"slot_id": slot_id},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        rid = json.loads(post_resp.data)["reservation_id"]

        resp = client.delete(
            f"/api/reservations/{rid}",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 204

        resp2 = client.get(
            f"/api/reservations/{rid}",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp2.status_code == 404

    def test_delete_wrong_key(self, client):
        """DELETE with a different user's key should return 403."""
        slot_id = _free_slot_id(client)
        post_resp = client.post(
            "/api/reservations",
            json={"slot_id": slot_id},
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        rid = json.loads(post_resp.data)["reservation_id"]

        resp = client.delete(
            f"/api/reservations/{rid}",
            headers={"swimapi-api-key": "customer-api-key2"}
        )
        assert resp.status_code == 403

    def test_delete_missing(self, client):
        """DELETE for a nonexistent reservation ID should return 404."""
        resp = client.delete(
            "/api/reservations/999999",
            headers={"swimapi-api-key": "customer-api-key1"}
        )
        assert resp.status_code == 404
