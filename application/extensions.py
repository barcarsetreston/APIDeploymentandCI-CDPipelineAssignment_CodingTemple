"""Flask extension instances, created here (uninitialized) so that models,
schemas, and blueprints can all import them without circular imports. They
are bound to the actual Flask app inside create_app() via .init_app().
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()
