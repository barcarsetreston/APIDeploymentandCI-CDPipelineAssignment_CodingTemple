from application.extensions import ma
from application.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
