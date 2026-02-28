import pytest
from datetime import datetime, timedelta
from swimapi import create_app
from swimapi.models import db, User, Resource, Timeslot, Reservation


def _populate_db():
    # ── Users ────────────────────────────────────────────────────────────
    admin = User(
        name="Admin User",
        email="admin@swimapi.local",
        api_key="admin-api-key",
        user_type="admin",
    )
    customers = [
        User(name="Alice Virtanen",  email="alice@example.com",  api_key="customer-api-key1", user_type="customer"),
        User(name="Bob Mäkinen",     email="bob@example.com",    api_key="customer-api-key2", user_type="customer"),
        User(name="Carol Korhonen",  email="carol@example.com",  api_key="customer-api-key3", user_type="customer"),
        User(name="David Leinonen",  email="david@example.com",  api_key="customer-api-key4", user_type="customer"),
    ]
    db.session.add(admin)
    db.session.add_all(customers)
    db.session.flush()

    # ── Resources ────────────────────────────────────────────────────────
    resources = [
        Resource(name="50m Pool",         description="Olympic-size 50-metre pool",  resource_type="pool"),
        Resource(name="Children's Pool",  description="Shallow pool for kids",       resource_type="pool"),
        Resource(name="Finnish Sauna",    description="Traditional wood-heated sauna", resource_type="sauna"),
        Resource(name="Steam Room",       description="Steam sauna / höyrysauna",    resource_type="sauna"),
        Resource(name="Fitness Gym",      description="Full equipment gym",          resource_type="gym"),
    ]
    db.session.add_all(resources)
    db.session.flush()

    # ── Timeslots ────────────────────────────────────────────────────────
    BASE = datetime(2026, 2, 21, 8, 0)
    SLOT_LEN = timedelta(minutes=90)
    DAY = timedelta(days=1)

    timeslots = []
    for day_offset in range(7):
        day_start = BASE + day_offset * DAY
        for hour_offset in range(8):
            start = day_start + hour_offset * SLOT_LEN
            end = start + SLOT_LEN
            for res in resources:
                timeslots.append(Timeslot(resource_id=res.resource_id, start_time=start, end_time=end))

    db.session.add_all(timeslots)
    db.session.flush()

    # ── Reservations ─────────────────────────────────────────────────────
    sample_slots = timeslots[::15][:12]
    reservations = []
    for i, slot in enumerate(sample_slots):
        user = customers[i % len(customers)]
        reservations.append(Reservation(user_id=user.user_id, slot_id=slot.slot_id))

    db.session.add_all(reservations)
    db.session.commit()


@pytest.fixture
def client():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    ctx = app.app_context()
    ctx.push()

    db.drop_all()
    db.create_all()
    _populate_db()

    yield app.test_client()

    db.session.rollback()
    db.drop_all()
    db.session.remove()
    ctx.pop()
