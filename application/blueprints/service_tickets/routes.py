from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

from application.blueprints.service_tickets import service_tickets_bp
from application.blueprints.service_tickets.schemas import (
    service_ticket_schema,
    service_tickets_schema,
)
from application.extensions import db
from application.models import Customer, Mechanic, ServiceTicket


def _resolve_mechanics(mechanic_ids):
    """Look up Mechanic objects for a list of IDs.

    Returns (mechanics, missing_ids). Callers should 404 if missing_ids is
    non-empty.
    """
    if not mechanic_ids:
        return [], set()
    mechanics = db.session.execute(
        select(Mechanic).where(Mechanic.id.in_(mechanic_ids))
    ).scalars().all()
    found_ids = {m.id for m in mechanics}
    missing = set(mechanic_ids) - found_ids
    return mechanics, missing


@service_tickets_bp.route("/service-tickets", methods=["POST"])
def create_service_ticket():
    """
    Create a new service ticket
    ---
    tags:
      - Service Tickets
    summary: Create a new service ticket
    description: >
      Creates a new service ticket for a customer. Optionally accepts a
      list of mechanic_ids to assign mechanics to the ticket at creation
      time.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ServiceTicketPayload'
    responses:
      201:
        description: Service ticket created successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Validation error
      404:
        description: Referenced customer or one or more mechanic_ids not found
    """
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    mechanic_ids = ticket_data.pop("mechanic_ids", [])

    customer = db.session.get(Customer, ticket_data["customer_id"])
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    mechanics, missing = _resolve_mechanics(mechanic_ids)
    if missing:
        return jsonify({"error": f"Mechanic id(s) not found: {sorted(missing)}"}), 404

    new_ticket = ServiceTicket(**ticket_data)
    new_ticket.mechanics = mechanics

    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201


@service_tickets_bp.route("/service-tickets", methods=["GET"])
def get_service_tickets():
    """
    Retrieve all service tickets
    ---
    tags:
      - Service Tickets
    summary: Get all service tickets
    description: Returns every service ticket, including its customer and assigned mechanics.
    responses:
      200:
        description: A list of service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicketResponse'
    """
    tickets = db.session.execute(select(ServiceTicket)).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200


@service_tickets_bp.route("/service-tickets/<int:ticket_id>", methods=["GET"])
def get_service_ticket(ticket_id):
    """
    Retrieve a specific service ticket
    ---
    tags:
      - Service Tickets
    summary: Get a single service ticket by ID
    description: Returns one service ticket, including its customer and assigned mechanics.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: ID of the service ticket to retrieve
    responses:
      200:
        description: The requested service ticket
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      404:
        description: Service ticket not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/service-tickets/<int:ticket_id>", methods=["PUT"])
def update_service_ticket(ticket_id):
    """
    Update a specific service ticket
    ---
    tags:
      - Service Tickets
    summary: Update an existing service ticket
    description: >
      Updates the VIN, service date, description, customer, and/or full
      mechanic assignment list on an existing ticket. To add or remove a
      single mechanic without replacing the whole list, use the
      assign-mechanic / remove-mechanic endpoints instead.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: ID of the service ticket to update
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ServiceTicketPayload'
    responses:
      200:
        description: Updated service ticket
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Validation error
      404:
        description: Service ticket, referenced customer, or a mechanic_id not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    try:
        ticket_data = service_ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    mechanic_ids = ticket_data.pop("mechanic_ids", None)

    if "customer_id" in ticket_data:
        customer = db.session.get(Customer, ticket_data["customer_id"])
        if not customer:
            return jsonify({"error": "Customer not found."}), 404

    for key, value in ticket_data.items():
        setattr(ticket, key, value)

    if mechanic_ids is not None:
        mechanics, missing = _resolve_mechanics(mechanic_ids)
        if missing:
            return jsonify({"error": f"Mechanic id(s) not found: {sorted(missing)}"}), 404
        ticket.mechanics = mechanics

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/service-tickets/<int:ticket_id>", methods=["DELETE"])
def delete_service_ticket(ticket_id):
    """
    Delete a specific service ticket
    ---
    tags:
      - Service Tickets
    summary: Delete a service ticket
    description: Deletes a service ticket by ID.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: ID of the service ticket to delete
    responses:
      200:
        description: Service ticket deleted successfully
      404:
        description: Service ticket not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Service ticket id {ticket_id} successfully deleted."}), 200


@service_tickets_bp.route(
    "/service-tickets/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def assign_mechanic(ticket_id, mechanic_id):
    """
    Assign a mechanic to a service ticket
    ---
    tags:
      - Service Tickets
    summary: Assign a mechanic to a service ticket
    description: Adds the given mechanic to the given service ticket's assigned mechanics.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: ID of the service ticket
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: ID of the mechanic to assign
    responses:
      200:
        description: Mechanic assigned successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Mechanic is already assigned to this ticket
      404:
        description: Service ticket or mechanic not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"error": "Mechanic is already assigned to this ticket."}), 400

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route(
    "/service-tickets/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def remove_mechanic(ticket_id, mechanic_id):
    """
    Remove a mechanic from a service ticket
    ---
    tags:
      - Service Tickets
    summary: Remove a mechanic from a service ticket
    description: Removes the given mechanic from the given service ticket's assigned mechanics.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: ID of the service ticket
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: ID of the mechanic to remove
    responses:
      200:
        description: Mechanic removed successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Mechanic was not assigned to this ticket
      404:
        description: Service ticket or mechanic not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic is not assigned to this ticket."}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200
