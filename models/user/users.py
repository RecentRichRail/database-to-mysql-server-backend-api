from db import db
from datetime import datetime

class UsersModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    is_email_valid = db.Column(db.Boolean, unique=False)
    default_search_id = db.Column(db.Integer, db.ForeignKey("commands.id"), unique=False, nullable=False)
    user_theme = db.Column(db.String(80), nullable=False, default="coffee")
    requests = db.relationship("RequestsModel", back_populates="user", lazy="dynamic")
    datetime_of_create_on_database = db.Column(db.DateTime, unique=False, nullable=True, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}