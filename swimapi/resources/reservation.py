"""Reservation endpoints for managing user reservations on timeslots."""
from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, ValidationError, Draft7Validator
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, NotFound, UnsupportedMediaType

from ..models import db, Reservation  # pylint: disable=relative-beyond-top-level
from ..utils import require_auth, require_admin, get_current_user  # pylint: disable=relative-beyond-top-level


class ReservationCollection(Resource):
    """Operations on the collection of reservations."""

    def get(self):
        """Return a list of all reservations. Requires admin privileges."""
        require_admin()
        return [r.serialize() for r in Reservation.query.all()]

    def post(self):
        """Create a new reservation."""
        body = request.get_json(silent=True)
        if body is None:
            raise UnsupportedMediaType

        # Take user from API key
        user = get_current_user()

        try:
            validate(body, Reservation.post_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        reservation = Reservation()
        reservation.user_id = user.user_id
        reservation.slot_id = body["slot_id"]

        try:
            db.session.add(reservation)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise Conflict(description="This timeslot is already reserved.") from exc

        return reservation.serialize(), 201


class ReservationItem(Resource):
    """Operations on a single reservation."""

    def find_reservation_by_id(self, reservation_id):
        """Return the reservation with the given ID"""
        reservation = Reservation.query.get(reservation_id)
        if reservation is None:
            raise NotFound(description=f"Reservation {reservation_id} not found.")
        return reservation

    def get(self, reservation_id):
        """Return a single reservation by ID. Requires owner or admin."""
        reservation = self.find_reservation_by_id(reservation_id)
        require_auth(reservation.user)
        return reservation.serialize()

    def delete(self, reservation_id):
        """Delete a reservation. Requires owner or admin."""
        reservation = self.find_reservation_by_id(reservation_id)
        require_auth(reservation.user)
        db.session.delete(reservation)
        db.session.commit()
        return Response(status=204)
