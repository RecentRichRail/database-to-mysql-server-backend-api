from flask import Blueprint, request
from db import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from models import LoginAttemptModel, UsersModel

blp = Blueprint('login', __name__)

@blp.route("/apiv1/data/login_attempt", methods=['POST'])
def login_attempt():
    data = request.get_json()

    login_attempt = {
        "user_id": data.get('user_id', None),
        "is_authenticated": data.get('is_authenticated', False),
        "requested_resource": data.get('requested_resource', "Error"),
        "request_ip_source": data.get('request_ip_source', "Error"),
        "datetime_of_login_attempt": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            }

    print("Login attempt data = ", login_attempt)
    login_attempt_model = LoginAttemptModel(**login_attempt)
    try:
        db.session.add(login_attempt_model)
        db.session.commit()
        print("Login attempt recorded.")
        return {"message": "Login attempt recorded."}
    except SQLAlchemyError as e:
        print(e)
        print("Failed to record login attempt.")
        return {"message": "Failed to record login attempt."}