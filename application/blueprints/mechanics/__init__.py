from flask import Blueprint

mechanics_bp = Blueprint("mechanics", __name__)

from application.blueprints.mechanics import routes  # noqa: E402,F401
