from db import db
from datetime import datetime

class DevicesSerialNumberModel(db.Model):
    __tablename__ = "devices_serial_number"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    serial_number = db.Column(db.String(80), unique=True, nullable=False)
    unique_identifier_verification_key = db.Column(db.String(300), unique=True, nullable=False)
    datetime_of_create_on_database = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}