from db import db

class LoginAttemptModel(db.Model):
    __tablename__ = "login_attempt"

    login_attempt_id = db.Column(db.Integer, primary_key=True, unique=False, nullable=False, autoincrement=True)
    user_id = db.Column(db.String(80), db.ForeignKey("users.id"), unique=False, nullable=True)
    is_authenticated = db.Column(db.Boolean, unique=False)
    requested_resource = db.Column(db.String(500), unique=False)
    request_ip_source = db.Column(db.String(80), unique=False)
    datetime_of_login_attempt = db.Column(db.DateTime, unique=False, nullable=False)