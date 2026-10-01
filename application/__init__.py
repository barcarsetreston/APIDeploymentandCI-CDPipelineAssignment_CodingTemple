"""Application factory for the Mechanic Shop API.

Builds and configures the Flask app: extensions (SQLAlchemy, Marshmallow),
Swagger/Flasgger documentation, and blueprints, following the Application
Factory Pattern covered in the "Application Factory Pattern in Flask API
Development" lesson.
"""

from flask import Flask
from flasgger import Swagger

from application.extensions import db, ma
from config import config_by_name

# ---------------------------------------------------------------------------
# Swagger configuration
# ---------------------------------------------------------------------------
# Central "definitions" block holding the PayloadDefinition (what the client
# sends on POST/PUT) and ResponseDefinitions (what the API returns) for each
# resource. Individual route docstrings reference these via $ref so the
# shapes stay consistent and defined in exactly one place.

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Mechanic Shop API",
        "description": (
            "A RESTful API for managing a mechanic shop's customers, "
            "mechanics, and service tickets, built with Flask, "
            "SQLAlchemy, and Marshmallow."
        ),
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "bearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter a token as: Bearer <token>",
        }
    },
    "definitions": {
        "CustomerPayload": {
            "type": "object",
            "required": ["name", "email", "phone"],
            "properties": {
                "name": {"type": "string", "example": "Jane Doe"},
                "email": {"type": "string", "example": "jane@example.com"},
                "phone": {"type": "string", "example": "555-123-4567"},
            },
        },
        "CustomerResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Jane Doe"},
                "email": {"type": "string", "example": "jane@example.com"},
                "phone": {"type": "string", "example": "555-123-4567"},
            },
        },
        "MechanicPayload": {
            "type": "object",
            "required": ["name", "email", "phone", "address", "salary"],
            "properties": {
                "name": {"type": "string", "example": "Sam Wrench"},
                "email": {"type": "string", "example": "sam@shop.com"},
                "phone": {"type": "string", "example": "555-987-6543"},
                "address": {"type": "string", "example": "123 Garage Ave"},
                "salary": {"type": "number", "format": "float", "example": 55000.00},
            },
        },
        "MechanicResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Sam Wrench"},
                "email": {"type": "string", "example": "sam@shop.com"},
                "phone": {"type": "string", "example": "555-987-6543"},
                "address": {"type": "string", "example": "123 Garage Ave"},
                "salary": {"type": "number", "format": "float", "example": 55000.00},
            },
        },
        "ServiceTicketPayload": {
            "type": "object",
            "required": ["VIN", "service_date", "service_desc", "customer_id"],
            "properties": {
                "VIN": {"type": "string", "example": "1HGCM82633A004352"},
                "service_date": {
                    "type": "string",
                    "format": "date",
                    "example": "2026-09-16",
                },
                "service_desc": {
                    "type": "string",
                    "example": "Oil change and tire rotation",
                },
                "customer_id": {"type": "integer", "example": 1},
                "mechanic_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "example": [1, 2],
                    "description": "Optional list of mechanic IDs to assign to this ticket.",
                },
            },
        },
        "ServiceTicketResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "VIN": {"type": "string", "example": "1HGCM82633A004352"},
                "service_date": {
                    "type": "string",
                    "format": "date",
                    "example": "2026-09-16",
                },
                "service_desc": {
                    "type": "string",
                    "example": "Oil change and tire rotation",
                },
                "customer_id": {"type": "integer", "example": 1},
                "customer": {"$ref": "#/definitions/CustomerResponse"},
                "mechanics": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/MechanicResponse"},
                },
            },
        },
    },
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
}


def create_app(config_name="development"):
    """Build and configure the Flask app (the Application Factory)."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    Swagger(app, template=swagger_template, config=swagger_config)

    # Register blueprints
    from application.blueprints.customers import customers_bp
    from application.blueprints.mechanics import mechanics_bp
    from application.blueprints.service_tickets import service_tickets_bp

    app.register_blueprint(customers_bp)
    app.register_blueprint(mechanics_bp)
    app.register_blueprint(service_tickets_bp)

    # Create tables if they don't already exist. For a class project this
    # stands in for migrations; swap in Flask-Migrate/Alembic for a real
    # production app.
    with app.app_context():
        db.create_all()

    return app
