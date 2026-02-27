import pytest
from datetime import datetime, timedelta
from swimapi import create_app
from swimapi.models import db, User, Resource, Timeslot, Reservation

def populate():
    app = create_app()

    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

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
        db.session.flush()  # get IDs without committing

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

        # ── Timeslots — one week starting today, every 90 minutes ────────────
        BASE = datetime(2026, 2, 21, 8, 0)   # Saturday 08:00
        SLOT_LEN = timedelta(minutes=90)
        DAY = timedelta(days=1)

        timeslots = []
        for day_offset in range(7):
            day_start = BASE + day_offset * DAY
            for hour_offset in range(8):          # 08:00 – 20:30
                start = day_start + hour_offset * SLOT_LEN
                end   = start + SLOT_LEN
                for res in resources:
                    ts = Timeslot(resource_id=res.resource_id, start_time=start, end_time=end)
                    timeslots.append(ts)

        db.session.add_all(timeslots)
        db.session.flush()

        # ── Reservations — scatter a few across users / slots ────────────────
        sample_slots = timeslots[::15][:12]   # every 15th slot, up to 12

        reservations = []
        for i, slot in enumerate(sample_slots):
            user = customers[i % len(customers)]
            reservations.append(
                Reservation(user_id=user.user_id, slot_id=slot.slot_id)
            )

        db.session.add_all(reservations)
        db.session.commit()

        # ── Summary ──────────────────────────────────────────────────────────
        print("Database populated successfully!")
        print(f"  Users      : {User.query.count()} (1 admin + {len(customers)} customers)")
        print(f"  Resources  : {Resource.query.count()}")
        print(f"  Timeslots  : {Timeslot.query.count()}")
        print(f"  Reservations: {Reservation.query.count()}")
        print()
        print("API keys:")
        print(f"  admin  : {admin.api_key}")
        for c in customers:
            print(f"  {c.name:<18}: {c.api_key}")

@pytest.fixture
def client():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        populate()

        yield app.test_client()

        db.session.rollback()
        db.drop_all()
        db.session.remove()
