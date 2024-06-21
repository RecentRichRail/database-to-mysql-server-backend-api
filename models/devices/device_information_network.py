from db import db
from datetime import datetime

class DevicesNetworkModel(db.Model):
    __tablename__ = "devices_network"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    ip_address = db.Column(db.String(15), unique=False, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}