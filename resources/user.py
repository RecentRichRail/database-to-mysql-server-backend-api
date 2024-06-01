from flask import Blueprint, request, jsonify, current_app
import requests
from models import UsersModel, CommandsModel, BananaGameUserBananasModel, BananaGameLifetimeBananasModel, BananaGameButtonPressModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# from models import CommandsModel, BananaGameUserBananasModel, BananaGameLifetimeBananasModel, BananaGameButtonPressModel

blp = Blueprint('user', __name__)

def create_user_for_internal(user_sub):
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
        return user
    except SQLAlchemyError as e:
        print(e)

def create_user_banana_game_with_id(user_id):
    user_stats_bananas = {"id": user_id, "bananas": 0}
    user_stats_lifetime_bananas = {"id": user_id, "lifetime_bananas": 0}
    user_stats_button_press = {"id": user_id, "button_clicks": 0, "bananas_per_button_click": 1, "datetime_of_last_button_press": datetime.now().strftime('%Y%m%d%H%M%S')}

    user_stats_bananas_model = BananaGameUserBananasModel(**user_stats_bananas)
    user_stats_lifetime_bananas_model = BananaGameLifetimeBananasModel(**user_stats_lifetime_bananas)
    user_stats_button_press_model = BananaGameButtonPressModel(**user_stats_button_press)

    db.session.add(user_stats_bananas_model)
    db.session.add(user_stats_lifetime_bananas_model)
    db.session.add(user_stats_button_press_model)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        print(e)

@blp.route("/apiv1/data/user", methods=['POST'])
def get_user():
    jwt_token = request.json.get("jwt")

    response = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
    user_sub = response.json()

    user_query = UsersModel.query.filter_by(id=user_sub['sub']).first()

    if not user_query:
        user_query = create_user(user_sub)
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

@blp.route("/apiv1/data/create_user", methods=['POST'])
def create_user():
    payload = request.json.get("payload")

    user_query = UsersModel.query.filter_by(id=payload['sub']).first()

    if not user_query:
        print("Creating user account.")
        create_user_for_internal(payload)

    if not BananaGameUserBananasModel.query.filter_by(id=payload['sub']).first():
        print("Creating game account.")
        create_user_banana_game_with_id(payload['sub'])


    return {"id": payload['sub']}