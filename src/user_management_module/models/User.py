# User.py
from flask_security import UserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from src.utils.DbConstants import *
from extensions import db, ma as marshmallow
from src.user_management_module.models.Role import RoleSchema
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = TABLE_USER
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    repeat_password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean(), default=True)
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    roles = relationship('Role', secondary=TABLE_ROLE_USERS,
                         backref=backref(TABLE_ROLE, lazy='dynamic'), single_parent=True, uselist=True)
    first_name = db.Column(db.String(TEXT_LENGTH_PRIMARY))
    last_name = db.Column(db.String(TEXT_LENGTH_PRIMARY))
    middle_name = db.Column(db.String(TEXT_LENGTH_PRIMARY))
    created_on = db.Column(db.DateTime(), default=datetime.now())
    updated_on = db.Column(
        db.DateTime(), default=datetime.now(), onupdate=datetime.now())
    created_by = db.Column(JSONB(none_as_null=True))
    last_updated_by = db.Column(JSONB(none_as_null=True))
    salutation = db.Column(db.String(TEXT_LENGTH_PRIMARY))
    phone = db.Column(db.String(TEXT_LENGTH_PRIMARY))
    alternate_contact = db.Column(db.String(TEXT_LENGTH_PRIMARY))
    gender = db.Column(db.String(TEXT_LENGTH_PRIMARY))
    dob = db.Column(db.DateTime())
    address = db.Column(db.String)
    pincode = db.Column(db.Integer)
    state = db.Column(db.String)
    district = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    employee_code = db.Column(db.String)
    username = db.Column(db.String)
    log_id = Column(Integer, unique=True)
    
class SessionLog(db.Model):
    __tablename__ = TABLE_SESSION_LOG
    id = Column(Integer, primary_key=True)
    created_on = db.Column(db.DateTime(), default=datetime.now())
    updated_on = db.Column(
        db.DateTime(), onupdate=datetime.now())
    auth_token = Column(String(255), unique=True,
                        default=uuid.uuid4, nullable=False)
    user_id = Column('user_id', Integer(), ForeignKey(TABLE_USER+'.id'))
    logged_ip = Column(String(100))
    logged_browser = Column(String(TEXT_LENGTH_DESCRIPTION_PRIMARY))
    active = Column(Boolean())

# Response Data with some fields
class UserSchema(SQLAlchemyAutoSchema):
    roles = marshmallow.Nested(RoleSchema, many=True)
    class Meta:
        model = User
        include_fk = True
        sqla_session = db.session

user_schema = UserSchema()
users_schema = UserSchema(many=True)

USER_ONLY_SCHEMA_COLUMNS = ['id', 'email', 'salutation', 'first_name',
                            'middle_name', 'last_name',  'active', 'roles']

user_only_schema = UserSchema(only=(USER_ONLY_SCHEMA_COLUMNS))
users_only_schema = UserSchema(only=(USER_ONLY_SCHEMA_COLUMNS), many=True)

user_schema_for_reports = UserSchema(only=(USER_ONLY_SCHEMA_COLUMNS), exclude=('roles',))
users_schema_for_reports = UserSchema(only=(USER_ONLY_SCHEMA_COLUMNS), exclude=('roles',), many=True)
