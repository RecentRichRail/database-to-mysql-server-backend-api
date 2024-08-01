from flask import Blueprint, request, jsonify, current_app
import requests
from models import BananaGameUserBananasModel, BananaGameLifetimeBananasModel, BananaGameButtonPressModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from models import CommandsModel

blp = Blueprint('banana_game', __name__)

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