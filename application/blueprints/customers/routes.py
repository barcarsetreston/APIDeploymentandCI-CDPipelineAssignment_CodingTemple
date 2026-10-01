from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

from application.blueprints.customers import customers_bp
from application.blueprints.customers.schemas import customer_schema, customers_schema
from application.extensions import db
from application.models import Customer


@customers_bp.route("/customers", methods=["POST"])
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    summary: Create a new customer
    description: Creates a new customer record. The email address must be unique.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerPayload'
    responses:
      201:
        description: Customer created successfully
        schema:
          $ref: '#/definitions/CustomerResponse'
        examples:
          application/json:
            id: 1
            name: "Jane Doe"
            email: "jane@example.com"
            phone: "555-123-4567"
      400:
        description: Validation error, or a customer with this email already exists
    """
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    existing = db.session.execute(
        select(Customer).where(Customer.email == customer_data["email"])
    ).scalar_one_or_none()
    if existing:
        return jsonify({"error": "A customer with this email already exists."}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


@customers_bp.route("/customers", methods=["GET"])
def get_customers():
    """
    Retrieve all customers
    ---
    tags:
      - Customers
    summary: Get all customers
    description: Returns a list of every customer in the system.
    responses:
      200:
        description: A list of customers
        schema:
          type: array
          items:
            $ref: '#/definitions/CustomerResponse'
    """
    customers = db.session.execute(select(Customer)).scalars().all()
    return customers_schema.jsonify(customers), 200


@customers_bp.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """
    Retrieve a specific customer
    ---
    tags:
      - Customers
    summary: Get a single customer by ID
    description: Returns one customer record matching the given ID.
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
        description: ID of the customer to retrieve
    responses:
      200:
        description: The requested customer
        schema:
          $ref: '#/definitions/CustomerResponse'
      404:
        description: Customer not found
    """
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    return customer_schema.jsonify(customer), 200


@customers_bp.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    """
    Update a specific customer
    ---
    tags:
      - Customers
    summary: Update an existing customer
    description: Updates one or more fields on an existing customer.
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
        description: ID of the customer to update
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerPayload'
    responses:
      200:
        description: Updated customer
        schema:
          $ref: '#/definitions/CustomerResponse'
      400:
        description: Validation error, or the new email is already in use
      404:
        description: Customer not found
    """
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "email" in customer_data and customer_data["email"] != customer.email:
        existing = db.session.execute(
            select(Customer).where(Customer.email == customer_data["email"])
        ).scalar_one_or_none()
        if existing:
            return jsonify({"error": "A customer with this email already exists."}), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


@customers_bp.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    """
    Delete a specific customer
    ---
    tags:
      - Customers
    summary: Delete a customer
    description: Deletes a customer and all of their associated service tickets.
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
        description: ID of the customer to delete
    responses:
      200:
        description: Customer deleted successfully
      404:
        description: Customer not found
    """
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer id {customer_id} successfully deleted."}), 200
