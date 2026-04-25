"""HTTP routes for triggering auxiliary maintenance tasks."""

import requests
from flask import Blueprint, jsonify, request
from maintenance_service import (
    cleanup_expired_timeslots,
    generate_future_timeslots,
    run_full_cycle,
)

auxiliary_bp = Blueprint("auxiliary", __name__)


def _extract_upstream_error(http_err):
    """Extract useful error information from an upstream HTTP error."""
    response = http_err.response
    if response is None:
        return "Upstream API request failed.", 502

    message = response.text or "Upstream API request failed."
    try:
        parsed = response.json()
        if isinstance(parsed, dict):
            message = parsed.get("message") or parsed.get("description") or message
        else:
            message = str(parsed)
    except ValueError:
        pass

    return message, response.status_code


@auxiliary_bp.route("/health", methods=["GET"])
def health():
    """Return a lightweight health response."""
    return jsonify({"status": "ok"}), 200


@auxiliary_bp.route("/cleanup", methods=["POST"])
def cleanup():
    """Run expired timeslot cleanup and return deletion count."""
    try:
        deleted = cleanup_expired_timeslots()
        return jsonify({"deleted_timeslots": deleted})
    except requests.exceptions.HTTPError as http_err:
        message, status_code = _extract_upstream_error(http_err)
        return jsonify({"error": message}), status_code
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Upstream API unavailable: {req_err}"}), 502


@auxiliary_bp.route("/generate", methods=["POST"])
def generate():
    """Generate future timeslots for the requested day horizon."""
    data = request.get_json(silent=True) or {}
    days_ahead = data.get("days_ahead", 7)

    try:
        created = generate_future_timeslots(days_ahead)
        return jsonify({"created_timeslots": created})
    except requests.exceptions.HTTPError as http_err:
        message, status_code = _extract_upstream_error(http_err)
        return jsonify({"error": message}), status_code
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Upstream API unavailable: {req_err}"}), 502


@auxiliary_bp.route("/run-cycle", methods=["POST"])
def run_cycle():
    """Run cleanup and generation in one maintenance cycle."""
    data = request.get_json(silent=True) or {}
    days_ahead = data.get("days_ahead", 7)

    try:
        result = run_full_cycle(days_ahead)
        return jsonify(result)
    except requests.exceptions.HTTPError as http_err:
        message, status_code = _extract_upstream_error(http_err)
        return jsonify({"error": message}), status_code
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Upstream API unavailable: {req_err}"}), 502
