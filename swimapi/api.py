"""API initialisation: creates the Api instance and registers all resources."""

from flask_restful import Api

from .resources.user import UserCollection, UserItem, AdminUserCollection
from .resources.resources import ResourceCollection, ResourceItem
from .resources.timeslot import TimeslotCollection, TimeslotItem
from .resources.reservation import ReservationCollection, ReservationItem


def init_api(app):
    """Attach flask-restful Api to app and register all resource routes."""
    api = Api(app)

    api.add_resource(UserCollection, "/api/users")
    api.add_resource(UserItem, "/api/users/<int:user_id>")
    api.add_resource(AdminUserCollection, "/api/admin/users")
    api.add_resource(ResourceCollection, "/api/resources")
    api.add_resource(ResourceItem, "/api/resources/<int:resource_id>")
    api.add_resource(TimeslotCollection, "/api/timeslots")
    api.add_resource(TimeslotItem, "/api/timeslots/<int:slot_id>")
    api.add_resource(ReservationCollection, "/api/reservations")
    api.add_resource(ReservationItem, "/api/reservations/<int:reservation_id>")
