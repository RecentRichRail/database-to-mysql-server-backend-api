from flask import Blueprint, request, jsonify, current_app
import requests
from models import UsersModel
from db import db
from sqlalchemy.exc import SQLAlchemyError

from models import CommandsModel

blp = Blueprint('user', __name__)

@blp.route("/apiv1/data/user", methods=['POST'])
def get_user():
    jwt_token = request.json.get("jwt")

    response = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
    user_sub = response.json()

    user_query = UsersModel.query.filter_by(id=user_sub['sub']).first()

    if not user_query:
        print("User not found")
        cmd_query = CommandsModel.query.filter_by(category="default_search").first()

        user = {"id": user_sub['sub'],
            "email": user_sub.get('email')['address'],
            "is_email_valid": user_sub.get('email')['is_verified'],
            "default_search_id": cmd_query.id}

        user_model = UsersModel(**user)

        try:
            db.session.add(user_model)
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
    else:
        user = {"id": user_query.id,
            "email": user_query.email,
            "is_email_valid": user_query.is_email_valid,
            "default_search_id": user_query.default_search_id}

    return jsonify(user_query.to_dict())

@blp.route("/apiv1/data/user/default_search", methods=['POST'])
def get_user_default_search():
    jwt_token = request.json.get("jwt")

    response = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
    user_sub = response.json()

    user_query = UsersModel.query.filter_by(id=user_sub['sub']).first()
    user_default_command_query = CommandsModel.query.filter_by(id=user_query.default_search_id).first()

    print("User default command = ", user_default_command_query.to_dict())
    
    if user_default_command_query:
        return user_default_command_query.to_dict()
    else:
        return {"message": "Something went wrong with userdata"}