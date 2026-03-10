from datetime import datetime
from marshmallow import Schema, fields

class MessageSchema(Schema):
    sender = fields.Str(required=True)
    text = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True, default=datetime.utcnow)

class ChatSchema(Schema):
    id = fields.Str(dump_only=True) 
    user_id = fields.Str(required=True)
    messages = fields.List(fields.Nested(MessageSchema), required=True)
    created_at = fields.DateTime(dump_only=True, default=datetime.utcnow)
    shareable_link = fields.Str(dump_only=True)
    archived = fields.Bool(dump_only=True, default=False)   
    archived_at = fields.DateTime(dump_only=True)           

