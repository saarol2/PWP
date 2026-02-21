"""Timeslot endpoints for managing time slots on bookable resources."""
from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, ValidationError, draft7_format_checker
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, NotFound, UnsupportedMediaType

from ..models import db, Timeslot
from ..utils import require_admin


class TimeslotCollection(Resource):
    """Operations on the collection of timeslots."""

    def get(self):
        """Return a list of all timeslots."""
        return [t.serialize() for t in Timeslot.query.all()]

    def post(self):
        """Create a new timeslot. Requires admin privileges."""
        require_admin()

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Timeslot.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise BadRequest(description=str(e))

        timeslot = Timeslot()
        timeslot.deserialize(request.json)

        try:
            db.session.add(timeslot)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(description="Failed to create timeslot due to a conflict.")

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

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Timeslot.json_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise BadRequest(description=str(e))

        timeslot.deserialize(request.json)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(description="Failed to update timeslot due to a conflict.")

        return Response(status=204)

    def delete(self, slot_id):
        """Delete a timeslot by ID. Requires admin privileges."""
        require_admin()
        timeslot = self.find_timeslot_by_id(slot_id)
        db.session.delete(timeslot)
        db.session.commit()
        return Response(status=204)
