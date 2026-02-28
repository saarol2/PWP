"""Resource endpoints for managing bookable resources (pools, saunas, gyms)."""
from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, ValidationError, Draft7Validator
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType, NotFound

from ..models import db, Resource as ResourceModel
from ..utils import require_admin


class ResourceCollection(Resource):
    """Operations on the collection of bookable resources."""

    def get(self):
        """Return a list of all resources."""
        return [r.serialize() for r in ResourceModel.query.all()]

    def post(self):
        """Create a new resource. Requires admin privileges."""
        require_admin()

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, ResourceModel.json_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e))

        resource = ResourceModel()
        resource.deserialize(request.json)

        db.session.add(resource)
        db.session.commit()

        return resource.serialize(), 201


class ResourceItem(Resource):
    """Operations on a single bookable resource."""

    def find_resource_by_id(self, resource_id):
        """Return the resource with the given ID or raise 404."""
        resource = ResourceModel.query.get(resource_id)
        if resource is None:
            raise NotFound(description=f"Resource {resource_id} not found.")
        return resource

    def get(self, resource_id):
        """Return a single resource by ID."""
        return self.find_resource_by_id(resource_id).serialize()

    def put(self, resource_id):
        """Replace an existing resource's data. Requires admin privileges."""
        require_admin()
        resource = self.find_resource_by_id(resource_id)

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, ResourceModel.json_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e))

        resource.deserialize(request.json)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(description="A resource with these details already exists.")

        return Response(status=204)

    def delete(self, resource_id):
        """Delete a resource by ID. Requires admin privileges."""
        require_admin()
        resource = self.find_resource_by_id(resource_id)
        db.session.delete(resource)
        db.session.commit()
        return Response(status=204)
