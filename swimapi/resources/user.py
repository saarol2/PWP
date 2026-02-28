"""User endpoints for managing user accounts."""
import secrets
from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, ValidationError, Draft7Validator
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType, NotFound

from ..models import db, User  # pylint: disable=relative-beyond-top-level
from ..utils import require_auth  # pylint: disable=relative-beyond-top-level


class UserCollection(Resource):
    """Operations on the collection of users."""

    def get(self):
        """Return a list of all users."""
        return [u.serialize() for u in User.query.all()]

    def post(self):
        """Create a new user and return it with api_key."""
        body = request.get_json(silent=True)
        if not body:
            raise UnsupportedMediaType

        try:
            validate(body, User.json_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        user = User(api_key=secrets.token_hex(32))
        user.deserialize(body)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise Conflict(
                description=f"User with email '{body['email']}' already exists."
            ) from exc

        body = user.serialize()
        body["api_key"] = user.api_key
        return body, 201


class UserItem(Resource):
    """Operations on a single user."""

    def find_user_by_id(self, user_id):
        """Return the user with the given ID or raise 404."""
        user = User.query.get(user_id)
        if user is None:
            raise NotFound(description=f"User {user_id} not found.")
        return user

    def get(self, user_id):
        """Return a single user by ID."""
        return self.find_user_by_id(user_id).serialize()

    def put(self, user_id):
        """Replace an existing user's data."""
        user = self.find_user_by_id(user_id)
        require_auth(user)

        body = request.get_json(silent=True)
        if not body:
            raise UnsupportedMediaType

        try:
            validate(body, User.json_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        user.deserialize(body)

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise Conflict(
                description=f"User with email '{body['email']}' already exists."
            ) from exc

        return Response(status=204)

    def delete(self, user_id):
        """Delete a user by ID."""
        user = self.find_user_by_id(user_id)
        require_auth(user)
        db.session.delete(user)
        db.session.commit()
        return Response(status=204)


class AdminUserCollection(Resource):
    """Endpoint for creating admin users."""

    def post(self):
        """Create a new admin user."""
        body = request.get_json(silent=True)
        if not body:
            raise UnsupportedMediaType

        try:
            validate(body, User.json_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        user = User(api_key=secrets.token_hex(32), user_type="admin")
        user.deserialize(body)
        user.user_type = "admin"

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise Conflict(
                description=f"User with email '{body['email']}' already exists."
            ) from exc

        body = user.serialize()
        body["api_key"] = user.api_key
        return body, 201
