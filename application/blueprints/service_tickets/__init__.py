from flask import Blueprint

service_tickets_bp = Blueprint("service_tickets", __name__)

from application.blueprints.service_tickets import routes  # noqa: E402,F401
