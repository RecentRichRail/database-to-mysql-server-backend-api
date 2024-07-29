from db import db

class RequestsModel(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True, unique=False, nullable=False, autoincrement=True)
    original_request = db.Column(db.String(500), nullable=False)
    prefix = db.Column(db.String(500), unique=False)
    search_query = db.Column(db.String(500), unique=False)
    encoded_query = db.Column(db.String(500), unique=False)
    is_search = db.Column(db.Boolean, unique=False, nullable=False)
    command_id = db.Column(db.Integer, db.ForeignKey("commands.id"), unique=False, nullable=False)
    command = db.relationship("CommandsModel", back_populates="requests")
    user_id = db.Column(db.String(80), db.ForeignKey("users.id"), unique=False, nullable=False)
    user = db.relationship("UsersModel", back_populates="requests")
    datetime_of_request = db.Column(db.DateTime, unique=False, nullable=False)