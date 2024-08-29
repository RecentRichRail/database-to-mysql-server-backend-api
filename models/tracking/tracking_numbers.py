from db import db
from datetime import datetime

class TrackingNumbersModel(db.Model):
    __tablename__ = "tracking_numbers"

    id = db.Column(db.Integer, primary_key=True, unique=False, nullable=False, autoincrement=True)
    tracking_number = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey("users.id"), unique=False, nullable=False)
    is_active = db.Column(db.Boolean)
    note = db.Column(db.String(5000), nullable=True, default="Package Description")
    datetime_of_create_on_database = db.Column(db.DateTime, unique=False, nullable=True, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}