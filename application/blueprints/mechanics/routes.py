from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

from application.blueprints.mechanics import mechanics_bp
from application.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from application.extensions import db
from application.models import Mechanic


@mechanics_bp.route("/mechanics", methods=["POST"])
def create_mechanic():
    """
    Create a new mechanic
    ---
    tags:
      - Mechanics
    summary: Create a new mechanic
    description: Creates a new mechanic record. The email address must be unique.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicPayload'
    responses:
      201:
        description: Mechanic created successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
        examples:
          application/json:
            id: 1
            name: "Sam Wrench"
            email: "sam@shop.com"
            phone: "555-987-6543"
            address: "123 Garage Ave"
            salary: 55000.00
      400:
        description: Validation error, or a mechanic with this email already exists
    """
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    existing = db.session.execute(
        select(Mechanic).where(Mechanic.email == mechanic_data["email"])
    ).scalar_one_or_none()
    if existing:
        return jsonify({"error": "A mechanic with this email already exists."}), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


@mechanics_bp.route("/mechanics", methods=["GET"])
def get_mechanics():
    """
    Retrieve all mechanics
    ---
    tags:
      - Mechanics
    summary: Get all mechanics
    description: Returns a list of every mechanic in the system.
    responses:
      200:
        description: A list of mechanics
        schema:
          type: array
          items:
            $ref: '#/definitions/MechanicResponse'
    """
    mechanics = db.session.execute(select(Mechanic)).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route("/mechanics/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
    """
    Retrieve a specific mechanic
    ---
    tags:
      - Mechanics
    summary: Get a single mechanic by ID
    description: Returns one mechanic record matching the given ID.
    parameters:
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: ID of the mechanic to retrieve
    responses:
      200:
        description: The requested mechanic
        schema:
          $ref: '#/definitions/MechanicResponse'
      404:
        description: Mechanic not found
    """
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    return mechanic_schema.jsonify(mechanic), 200


@mechanics_bp.route("/mechanics/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    """
    Update a specific mechanic
    ---
    tags:
      - Mechanics
    summary: Update an existing mechanic
    description: Updates one or more fields on an existing mechanic.
    parameters:
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: ID of the mechanic to update
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicPayload'
    responses:
      200:
        description: Updated mechanic
        schema:
          $ref: '#/definitions/MechanicResponse'
      400:
        description: Validation error, or the new email is already in use
      404:
        description: Mechanic not found
    """
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "email" in mechanic_data and mechanic_data["email"] != mechanic.email:
        existing = db.session.execute(
            select(Mechanic).where(Mechanic.email == mechanic_data["email"])
        ).scalar_one_or_none()
        if existing:
            return jsonify({"error": "A mechanic with this email already exists."}), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanics_bp.route("/mechanics/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
    """
    Delete a specific mechanic
    ---
    tags:
      - Mechanics
    summary: Delete a mechanic
    description: Deletes a mechanic and unassigns them from any service tickets.
    parameters:
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: ID of the mechanic to delete
    responses:
      200:
        description: Mechanic deleted successfully
      404:
        description: Mechanic not found
    """
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic id {mechanic_id} successfully deleted."}), 200
