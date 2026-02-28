"""Timeslot endpoints for managing time slots on bookable resources."""
from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, ValidationError, Draft7Validator
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, NotFound, UnsupportedMediaType

from ..models import db, Timeslot  # pylint: disable=relative-beyond-top-level
from ..utils import require_admin  # pylint: disable=relative-beyond-top-level


class TimeslotCollection(Resource):
    """Operations on the collection of timeslots."""

    def get(self):
        """Return a list of all timeslots."""
        return [t.serialize() for t in Timeslot.query.all()]

    def post(self):
        """Create a new timeslot. Requires admin privileges."""
        require_admin()

        body = request.get_json(silent=True)
        if not body:
            raise UnsupportedMediaType

        try:
            validate(body, Timeslot.json_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        timeslot = Timeslot()
        timeslot.deserialize(body)

        try:
            db.session.add(timeslot)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise Conflict(description="Failed to create timeslot due to a conflict.") from exc

        return timeslot.serialize(), 201


class TimeslotItem(Resource):
    """Operations on a single timeslot."""

    def find_timeslot_by_id(self, slot_id):
        """Return the timeslot with the given ID"""
        timeslot = Timeslot.query.get(slot_id)
        if timeslot is None:
            raise NotFound(description=f"Timeslot {slot_id} not found.")
        return timeslot

    def get(self, slot_id):
        """Return a single timeslot by ID."""
        return self.find_timeslot_by_id(slot_id).serialize()

    def put(self, slot_id):
        """Replace an existing timeslot's data. Requires admin privileges."""
        require_admin()
        timeslot = self.find_timeslot_by_id(slot_id)

        body = request.get_json(silent=True)
        if not body:
            raise UnsupportedMediaType

        try:
            validate(body, Timeslot.json_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        timeslot.deserialize(body)

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise Conflict(description="Failed to update timeslot due to a conflict.") from exc

        return Response(status=204)

    def delete(self, slot_id):
        """Delete a timeslot by ID. Requires admin privileges."""
        require_admin()
        timeslot = self.find_timeslot_by_id(slot_id)
        db.session.delete(timeslot)
        db.session.commit()
        return Response(status=204)
