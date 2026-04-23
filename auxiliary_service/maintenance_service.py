from datetime import datetime, timedelta, timezone
from client import get_timeslots, delete_timeslot, get_resources, create_timeslot
from config import DEFAULT_DAYS_AHEAD


def _parse_api_datetime(value):
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def _to_api_datetime(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc).replace(microsecond=0)
    return value.isoformat().replace("+00:00", "Z")


def cleanup_expired_timeslots():
    timeslots = get_timeslots()
    now = datetime.now(timezone.utc)

    deleted = 0

    for slot in timeslots:
        end_time = _parse_api_datetime(slot["end_time"])

        if end_time < now:
            delete_timeslot(slot["slot_id"])
            deleted += 1

    return deleted


def generate_future_timeslots(days_ahead=DEFAULT_DAYS_AHEAD):
    resources = get_resources()
    timeslots = get_timeslots()

    existing = {
        (
            slot["resource_id"],
            _to_api_datetime(_parse_api_datetime(slot["start_time"])),
            _to_api_datetime(_parse_api_datetime(slot["end_time"])),
        )
        for slot in timeslots
    }

    created = 0
    now = datetime.now(timezone.utc)

    for resource in resources:
        for day in range(days_ahead):
            base = now + timedelta(days=day)

            # esimerkki: 8-20 väliltä tunnin slotit
            for hour in range(8, 20):
                start = base.replace(hour=hour, minute=0, second=0, microsecond=0)
                end = start + timedelta(hours=1)

                key = (
                    resource["resource_id"],
                    _to_api_datetime(start),
                    _to_api_datetime(end),
                )

                if key not in existing:
                    payload = {
                        "resource_id": resource["resource_id"],
                        "start_time": _to_api_datetime(start),
                        "end_time": _to_api_datetime(end),
                    }

                    create_timeslot(payload)
                    created += 1

    return created


def run_full_cycle(days_ahead=DEFAULT_DAYS_AHEAD):
    deleted = cleanup_expired_timeslots()
    created = generate_future_timeslots(days_ahead)

    return {
        "deleted_timeslots": deleted,
        "created_timeslots": created,
        "status": "completed",
    }
