"""SQLAlchemy models for the Mechanic Shop API.

These map directly to the class ERD provided in the "Understanding ORMs
and SQLAlchemy Relationships" lesson:

    customers (1) ----< service_tickets >---- (M) mechanics

- A Customer can have many ServiceTickets (one-to-many).
- A ServiceTicket can have many Mechanics, and a Mechanic can work many
  ServiceTickets (many-to-many), implemented with the service_mechanics
  junction table.
"""

from datetime import date
from typing import List

from sqlalchemy import Column, Float, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.extensions import db


# Junction table reconciling the many-to-many relationship between
# ServiceTicket and Mechanic. This does not need its own full model class
# since it only holds the two foreign keys.
service_mechanics = Table(
    "service_mechanics",
    db.Model.metadata,
    Column("ticket_id", ForeignKey("service_tickets.id"), primary_key=True),
    Column("mechanic_id", ForeignKey("mechanics.id"), primary_key=True),
)


class Customer(db.Model):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # One-to-many: one customer -> many service tickets.
    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)

    # Many-to-many: a mechanic can be assigned to many service tickets.
    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        secondary=service_mechanics, back_populates="mechanics"
    )


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(nullable=False)
    service_desc: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    # Many-to-one: each ticket belongs to exactly one customer.
    customer: Mapped["Customer"] = relationship(back_populates="service_tickets")

    # Many-to-many: a ticket can require multiple mechanics.
    mechanics: Mapped[List["Mechanic"]] = relationship(
        secondary=service_mechanics, back_populates="service_tickets"
    )
