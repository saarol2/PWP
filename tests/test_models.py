"""Unit tests for swimapi model serialize/deserialize/schema methods."""
from datetime import datetime
from swimapi.models import User, Resource, Timeslot, Reservation


class TestUser:
    """Tests for the User model."""

    def test_serialize(self):
        """serialize() should return a dict with all user fields."""
        user = User(
            user_id=1,
            name="Test User",
            email="test@example.com",
            user_type="customer",
        )
        serialized = user.serialize()
        assert serialized["user_id"] == 1
        assert serialized["name"] == "Test User"
        assert serialized["email"] == "test@example.com"
        assert serialized["user_type"] == "customer"

    def test_deserialize(self):
        """deserialize() should update name and email from a dict."""
        user = User()
        user.name = "old"

        data = {
            "name": "new",
            "email": "new@test.com"
        }

        user.deserialize(data)

        assert user.name == "new"
        assert user.email == "new@test.com"

    def test_json_schema(self):
        """json_schema() should require name and email as strings."""
        schema = User.json_schema()
        assert schema["type"] == "object"
        assert "required" in schema
        assert "name" in schema["required"]
        assert "email" in schema["required"]

        props = schema["properties"]
        assert props["name"]["type"] == "string"
        assert props["email"]["type"] == "string"


class TestResource:
    """Tests for the Resource model."""

    def test_serialize(self):
        """serialize() should return a dict with all resource fields."""
        resource = Resource(
            resource_id=1,
            name="Test Pool",
            description="A test pool",
            resource_type="pool"
        )
        serialized = resource.serialize()
        assert serialized["resource_id"] == 1
        assert serialized["name"] == "Test Pool"
        assert serialized["description"] == "A test pool"
        assert serialized["resource_type"] == "pool"

    def test_deserialize(self):
        """deserialize() should update name, description and resource_type."""
        resource = Resource()
        resource.name = "old"

        data = {
            "name": "new",
            "description": "A new resource",
            "resource_type": "sauna"
        }

        resource.deserialize(data)

        assert resource.name == "new"
        assert resource.description == "A new resource"
        assert resource.resource_type == "sauna"

    def test_json_schema(self):
        """json_schema() should require name and resource_type as strings."""
        schema = Resource.json_schema()
        assert schema["type"] == "object"
        assert "required" in schema
        assert "name" in schema["required"]
        assert "resource_type" in schema["required"]

        props = schema["properties"]
        assert props["name"]["type"] == "string"
        assert props["description"]["type"] == "string"
        assert props["resource_type"]["type"] == "string"


class TestTimeslot:
    """Tests for the Timeslot model."""

    def test_serialize(self):
        """serialize() should return ISO-format datetime strings."""
        timeslot = Timeslot(
            slot_id=1,
            resource_id=2,
            start_time=datetime(2024, 1, 1, 8, 0, 0),
            end_time=datetime(2024, 1, 1, 9, 30, 0),
        )
        serialized = timeslot.serialize()
        assert serialized["slot_id"] == 1
        assert serialized["resource_id"] == 2
        assert serialized["start_time"] == "2024-01-01T08:00:00"
        assert serialized["end_time"] == "2024-01-01T09:30:00"

    def test_deserialize(self):
        """deserialize() should parse ISO strings into datetime objects."""
        timeslot = Timeslot()
        timeslot.start_time = None

        data = {
            "resource_id": 2,
            "start_time": "2024-01-01T08:00:00",
            "end_time": "2024-01-01T09:30:00",
        }

        timeslot.deserialize(data)

        assert timeslot.resource_id == 2
        assert timeslot.start_time == datetime(2024, 1, 1, 8, 0, 0)
        assert timeslot.end_time == datetime(2024, 1, 1, 9, 30, 0)

    def test_json_schema(self):
        """json_schema() should require resource_id, start_time and end_time."""
        schema = Timeslot.json_schema()
        assert schema["type"] == "object"
        assert "required" in schema
        assert "resource_id" in schema["required"]
        assert "start_time" in schema["required"]
        assert "end_time" in schema["required"]

        props = schema["properties"]
        assert props["resource_id"]["type"] == "integer"
        assert props["start_time"]["type"] == "string"
        assert props["end_time"]["type"] == "string"


class TestReservation:
    """Tests for the Reservation model."""

    def test_serialize(self):
        """serialize() should return a dict with reservation_id, user_id and slot_id."""
        reservation = Reservation(
            reservation_id=1,
            user_id=2,
            slot_id=3
        )
        serialized = reservation.serialize()
        assert serialized["reservation_id"] == 1
        assert serialized["user_id"] == 2
        assert serialized["slot_id"] == 3

    def test_deserialize(self):
        """deserialize() should update user_id and slot_id from a dict."""
        reservation = Reservation()
        reservation.reservation_id = 1

        data = {
            "user_id": 2,
            "slot_id": 3
        }

        reservation.deserialize(data)

        assert reservation.user_id == 2
        assert reservation.slot_id == 3

    def test_json_schema(self):
        """json_schema() should require user_id and slot_id as integers."""
        schema = Reservation.json_schema()
        assert schema["type"] == "object"
        assert "required" in schema
        assert "user_id" in schema["required"]
        assert "slot_id" in schema["required"]

        props = schema["properties"]
        assert props["user_id"]["type"] == "integer"
        assert props["slot_id"]["type"] == "integer"

    def test_post_schema(self):
        """post_schema() should require slot_id but not user_id."""
        schema = Reservation.post_schema()
        assert schema["type"] == "object"
        assert "required" in schema
        assert "slot_id" in schema["required"]
        assert "user_id" not in schema["required"]

        props = schema["properties"]
        assert props["slot_id"]["type"] == "integer"
