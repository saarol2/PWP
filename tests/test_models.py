import pytest
from datetime import datetime
from swimapi.models import User, Resource, Timeslot, Reservation

def test_serialize_user():
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

def test_deserialize_user():
    user = User()
    user.name = "old"

    data = {
        "name": "new",
        "email": "new@test.com"
    }

    user.deserialize(data)

    assert user.name == "new"
    assert user.email == "new@test.com"

def test_json_schema_user():
    schema = User.json_schema()
    assert "type" in schema and schema["type"] == "object"
    assert "required" in schema and "name" in schema["required"]
    assert "email" in schema["required"]
    assert "properties" in schema
    props = schema["properties"]
    assert "name" in props and props["name"]["type"] == "string"
    assert "email" in props and props["email"]["type"] == "string"

def test_serialize_resource():
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

def test_deserialize_resource():
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

def test_json_schema_resource():
    schema = Resource.json_schema()
    assert "type" in schema and schema["type"] == "object"
    assert "required" in schema and "name" in schema["required"]
    assert "resource_type" in schema["required"]
    assert "properties" in schema
    props = schema["properties"]
    assert "name" in props and props["name"]["type"] == "string"
    assert "description" in props and props["description"]["type"] == "string"
    assert "resource_type" in props and props["resource_type"]["type"] == "string"

def test_serialize_timeslot():
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

def test_deserialize_timeslot():
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

def test_json_schema_timeslot():
    schema = Timeslot.json_schema()
    assert "type" in schema and schema["type"] == "object"
    assert "required" in schema and "resource_id" in schema["required"]
    assert "start_time" in schema["required"]
    assert "end_time" in schema["required"]
    assert "properties" in schema
    props = schema["properties"]
    assert "resource_id" in props and props["resource_id"]["type"] == "integer"
    assert "start_time" in props and props["start_time"]["type"] == "string"
    assert "end_time" in props and props["end_time"]["type"] == "string"

def test_serialize_reservation():
    reservation = Reservation(
        reservation_id=1,
        user_id=2,
        slot_id=3
    )
    serialized = reservation.serialize()
    assert serialized["reservation_id"] == 1
    assert serialized["user_id"] == 2
    assert serialized["slot_id"] == 3

def test_deserialize_reservation():
    reservation = Reservation()
    reservation.reservation_id = 1

    data = {
        "user_id": 2,
        "slot_id": 3
    }

    reservation.deserialize(data)

    assert reservation.user_id == 2
    assert reservation.slot_id == 3

def test_json_schema_reservation():
    schema = Reservation.json_schema()
    assert "type" in schema and schema["type"] == "object"
    assert "required" in schema and "user_id" in schema["required"]
    assert "slot_id" in schema["required"]
    assert "properties" in schema
    props = schema["properties"]
    assert "user_id" in props and props["user_id"]["type"] == "integer"
    assert "slot_id" in props and props["slot_id"]["type"] == "integer"

def test_post_schema_reservation():
    schema = Reservation.post_schema()
    assert "type" in schema and schema["type"] == "object"
    assert "required" in schema and "slot_id" in schema["required"]
    assert "user_id" not in schema["required"]
    assert "properties" in schema
    props = schema["properties"]
    assert "slot_id" in props and props["slot_id"]["type"] == "integer"
