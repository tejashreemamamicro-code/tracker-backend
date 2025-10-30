# EmployeeLog.py
from extensions import db, ma as marshmallow
from sqlalchemy import Column, Integer, String, ForeignKey
from src.utils.DbConstants import *
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class EmployeeLog(db.Model):
    __tablename__ = TABLE_EMPLOYEE_LOG

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey(TABLE_USER+'.id', ondelete="CASCADE"))
    log_id = db.Column(Integer, ForeignKey('user.log_id'))
    loggin_logout = db.Column(JSONB(none_as_null=True))
    location_logs = db.Column(JSONB(none_as_null=True))
    leave = db.Column(JSONB(none_as_null=True))
    break_time = db.Column(JSONB(none_as_null=True))

class EmployeeLogSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EmployeeLog
        include_fk = True
        sqla_session = db.session

employee_log_schema = EmployeeLogSchema()
employees_log_schema = EmployeeLogSchema(many=True)
