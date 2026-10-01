from application.extensions import ma
from application.models import ServiceTicket


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        include_fk = True
        load_instance = False

    # Nested, read-only views of the related customer/mechanics so a GET
    # response shows more than just their IDs.
    customer = ma.Nested(
        "CustomerSchema", dump_only=True, only=("id", "name", "email", "phone")
    )
    mechanics = ma.Nested(
        "MechanicSchema",
        many=True,
        dump_only=True,
        only=("id", "name", "email", "phone"),
    )

    # Write-only field: a list of mechanic IDs to (dis)associate with this
    # ticket. Not a real column, so it's popped out in the route before the
    # ServiceTicket model is built/updated.
    mechanic_ids = ma.List(ma.Integer(), load_only=True, required=False)


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
