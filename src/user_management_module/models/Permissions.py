# Permissions.py
from extensions import db, ma as marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime
from src.utils.DbConstants import *
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

class Permissions(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    code = db.Column(db.String)
    module = db.Column(db.String)
    modulesequence = db.Column('modulesequence', db.Integer)
    permissionsequence = db.Column('permissionsequence', db.Integer)
    visibility = db.Column(db.Boolean, default = True)
    is_system_permission = db.Column(db.Boolean, default = False)
    created_on = db.Column(db.DateTime(), default=datetime.now())
    updated_on = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now())
    created_by = db.Column(JSONB(none_as_null=True))
    last_updated_by = db.Column(JSONB(none_as_null=True))
    is_active=Column(db.Boolean, default=True)

class PermissionsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Permissions
        sqla_session = db.session

permission_schema = PermissionsSchema()
permissions_schema = PermissionsSchema(many=True)
