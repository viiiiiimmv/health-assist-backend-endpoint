from datetime import datetime
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=False, validate=validate.Length(min=2))
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)
    auth_provider = fields.Str(required=True, validate=validate.OneOf(["local", "google"]))
    created_at = fields.DateTime(dump_only=True, default=datetime.utcnow)