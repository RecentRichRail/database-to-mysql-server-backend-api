from db import db
from datetime import datetime

class DevicesLastCheckInModel(db.Model):
    __tablename__ = "devices_last_check_in"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    time_last_check_in = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}