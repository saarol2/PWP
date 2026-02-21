"""Utility functions for authentication and authorization."""
import secrets

from flask import request
from werkzeug.exceptions import Forbidden
from .models import User

def require_auth(user):
    """Verify that the request's API key matches the given user.
    Expects a swimapi-api-key header with the user's API key.
    """
    token = request.headers.get("swimapi-api-key", "")
    if not token:
        raise Forbidden(description="Missing swimapi-api-key header.")
    if not secrets.compare_digest(token, user.api_key or ""):
        raise Forbidden(description="Invalid API key.")


def require_admin():
    """Look up the user by the API key in the request header and verify they are an admin."""
    token = request.headers.get("swimapi-api-key", "")
    if not token:
        raise Forbidden(description="Missing swimapi-api-key header.")
    user = User.query.filter_by(api_key=token).first()
    if user is None:
        raise Forbidden(description="Invalid API key.")
    if user.user_type != "admin":
        raise Forbidden(description="Admin privileges required.")
    return user
