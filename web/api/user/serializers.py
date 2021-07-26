from marshmallow import (fields, Schema, validates)
from marshmallow.validate import (Length, OneOf)
from .validators import validate_user_existance
from .user import SuperUser

class SuperUserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=Length(min=8))
    role = fields.Str(required=True, validate=OneOf(SuperUser.roles()))

    def __init__(self, new_user: bool=False, many=False):
        Schema.__init__(self, many=many)
        self.new_user = new_user

    @validates('email')
    def _validate_email_field(self, email):
        validate_user_existance(email, self.new_user)

    class meta:
        strict=True