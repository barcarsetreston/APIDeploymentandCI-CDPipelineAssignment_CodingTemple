from application.extensions import ma
from application.models import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = False


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
