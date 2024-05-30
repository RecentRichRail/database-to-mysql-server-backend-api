from flask import Blueprint, request, jsonify, current_app
import requests
from models import UsersModel, BananaGameUserBananasModel, BananaGameLifetimeBananasModel, BananaGameButtonPressModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from models import CommandsModel

blp = Blueprint('banana_game', __name__)

def create_user_with_id(user_id):
    user_stats_bananas = {"id": user_id, "bananas": 0}
    user_stats_lifetime_bananas = {"id": user_id, "lifetime_bananas": 0}
    user_stats_button_press = {"id": user_id, "button_clicks": 0, "bananas_per_button_click": 1, "datetime_of_last_button_press": datetime.now().strftime('%Y%m%d%H%M%S')}

    user_stats_bananas_model = BananaGameUserBananasModel(**user_stats_bananas)
    user_stats_lifetime_bananas_model = BananaGameLifetimeBananasModel(**user_stats_lifetime_bananas)
    user_stats_button_press_model = BananaGameButtonPressModel(**user_stats_button_press)

    db.session.add(user_stats_bananas_model)
    db.session.add(user_stats_lifetime_bananas_model)
    db.session.add(user_stats_button_press_model)

@blp.route("/apiv1/games/banana_clicker/is_user_allowed", methods=['POST'])
def is_user_allowed():
    jwt_token = request.json.get("jwt")

    response = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/verify_user_jwt", json={"jwt": jwt_token, "request_url": request.url, "request_ip_source": request.headers.get('X-Forwarded-For', request.remote_addr)})
    verification_result = response.json()
    user_id = verification_result['id']

    user_query = BananaGameUserBananasModel.query.filter_by(id=user_id).first()
    user_allowed_query = UsersModel.query.filter_by(id=user_id).first()

    if not user_allowed_query:
        return {"allowed": False}
    elif not user_query:
        print("User not found, Creating game account")
        create_user_with_id(user_id)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            return {"id": user_id, "allowed": True}
        
    return {"id": user_id, "allowed": True}

@blp.route("/apiv1/games/banana_clicker/get_user_stats", methods=['POST'])
def get_user_stats():
    user_id = request.json.get("id")

    user_query = BananaGameUserBananasModel.query.filter_by(id=user_id).first()

    return jsonify(user_query.to_dict())

@blp.route("/apiv1/games/banana_clicker/banana_button_action_press", methods=['POST'])
def banana_button_action_press():
    data = request.get_json()
    user_id = data.get('id')
    user_clicks = data.get('clicks')
    print(f"User Clicks: {user_clicks}")

    user_stats_bananas = BananaGameUserBananasModel.query.filter_by(id=user_id).first()
    user_stats_lifetime_bananas = BananaGameLifetimeBananasModel.query.filter_by(id=user_id).first()
    user_stats_button_press = BananaGameButtonPressModel.query.filter_by(id=user_id).first()

    bananas_per_click = user_stats_button_press.bananas_per_button_click

    user_stats_bananas.bananas += (user_clicks * bananas_per_click)
    print(f"Bananas: {user_stats_bananas.bananas}")
    user_stats_lifetime_bananas.lifetime_bananas += (user_clicks * bananas_per_click)
    user_stats_button_press.button_clicks += user_clicks
    user_stats_button_press.datetime_of_last_button_press = datetime.now().strftime('%Y%m%d%H%M%S')

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        print(e)

    return user_stats_bananas.to_dict()