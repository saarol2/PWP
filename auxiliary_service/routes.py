from flask import Blueprint, jsonify, request
from maintenance_service import (
    cleanup_expired_timeslots,
    generate_future_timeslots,
    run_full_cycle,
)

auxiliary_bp = Blueprint("auxiliary", __name__)


@auxiliary_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@auxiliary_bp.route("/cleanup", methods=["POST"])
def cleanup():
    deleted = cleanup_expired_timeslots()
    return jsonify({"deleted_timeslots": deleted})


@auxiliary_bp.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    days_ahead = data.get("days_ahead", 7)

    created = generate_future_timeslots(days_ahead)

    return jsonify({"created_timeslots": created})


@auxiliary_bp.route("/run-cycle", methods=["POST"])
def run_cycle():
    data = request.get_json(silent=True) or {}
    days_ahead = data.get("days_ahead", 7)

    result = run_full_cycle(days_ahead)

    return jsonify(result)
