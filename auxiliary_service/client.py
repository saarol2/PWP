import requests
from config import MAIN_API_URL, REQUEST_TIMEOUT, API_KEY_HEADER, ADMIN_API_KEY


def _auth_headers(include_if_empty=False):
    headers = {}
    if ADMIN_API_KEY or include_if_empty:
        headers[API_KEY_HEADER] = ADMIN_API_KEY
    return headers


def get_resources():
    resp = requests.get(
        f"{MAIN_API_URL}/resources",
        timeout=REQUEST_TIMEOUT,
        headers=_auth_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def get_timeslots():
    resp = requests.get(
        f"{MAIN_API_URL}/timeslots",
        timeout=REQUEST_TIMEOUT,
        headers=_auth_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def delete_timeslot(slot_id):
    resp = requests.delete(
        f"{MAIN_API_URL}/timeslots/{slot_id}",
        timeout=REQUEST_TIMEOUT,
        headers=_auth_headers(include_if_empty=True),
    )
    resp.raise_for_status()


def create_timeslot(payload):
    resp = requests.post(
        f"{MAIN_API_URL}/timeslots",
        json=payload,
        timeout=REQUEST_TIMEOUT,
        headers=_auth_headers(include_if_empty=True),
    )
    resp.raise_for_status()
    return resp.json()
