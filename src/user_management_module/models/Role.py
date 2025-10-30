# Role.py
from extensions import db, ma as marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_security import RoleMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from src.utils.DbConstants import *
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

class Role(db.Model, RoleMixin):
    __tablename__ = TABLE_ROLE
    id = Column(Integer(), primary_key=True)
    name = Column(String(80))
    role_code = Column(String(TEXT_LENGTH_DESCRIPTION_PRIMARY))
    description = Column(db.String(255))
    permissions = Column(ARRAY(String(TEXT_LENGTH_DESCRIPTION_SECONDARY)))
    is_system_role = Column(db.Boolean)
    is_active=Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime(timezone=True), default=db.func.now())
    last_updated_on = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now())
    created_by = db.Column(JSONB(none_as_null=True))
    last_updated_by = db.Column(JSONB(none_as_null=True))

class RolesUsers(db.Model):
    __tablename__ = TABLE_ROLE_USERS
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey(TABLE_USER+'.id'))
    role_id = Column('role_id', Integer(), ForeignKey(TABLE_ROLE+'.id'))
    created_on = db.Column(db.DateTime(timezone=True), default=db.func.now())
    last_updated_on = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now())
    created_by = db.Column(db.String(TEXT_LENGTH_DESCRIPTION_PRIMARY))
    last_updated_by = db.Column(db.String(TEXT_LENGTH_DESCRIPTION_PRIMARY))

# Schemas
class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        include_fk = True

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)
