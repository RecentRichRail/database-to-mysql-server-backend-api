from flask import Blueprint, request, jsonify, current_app
import requests
from models import UsersModel, CommandsModel, BananaGameUserBananasModel, BananaGameLifetimeBananasModel, BananaGameButtonPressModel, RequestsModel, TrackingNumbersModel, PermissionsModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from tracking_numbers import get_tracking_number

blp = Blueprint('user', __name__)

def create_user_for_internal(user_sub):
    print("User not found")
    cmd_query = CommandsModel.query.filter_by(category="default_search").first()

    user = {"id": user_sub['sub'],
        "email": user_sub.get('email')['address'],
        "is_email_valid": user_sub.get('email')['is_verified'],
        "default_search_id": cmd_query.id}
    
    permission = {"user_id": user_sub['sub'],
                  "permission_name": "commands",
                  "permission_level": 999}

    user_model = UsersModel(**user)
    user_permissions_model = PermissionsModel(**permission)

    db.session.add(user_model)
    
    try:
        db.session.commit()
        print("Internal account created for user")
        db.session.add(user_permissions_model)
        db.session.commit()
        print("Internal permissions created for user")
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
        print("Banana account created for user")
    except SQLAlchemyError as e:
        print(e)

@blp.route('/apiv1/data/user/change_theme', methods=['POST'])
def change_theme():
    selected_theme = request.json.get('theme')
    jwt_token = request.json.get("jwt_token")

    theme_list = ['coffee', 'mignight', 'dark']

    if str(selected_theme) not in theme_list:
        print("selected_theme")
        return {"message": "Error"}

    payload = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
    user_sub = payload.json()

    if user_sub:
        user_model = UsersModel.query.filter_by(id=user_sub['sub']).first()


        user_model.user_theme = selected_theme

        try:
            db.session.commit()
            print(selected_theme)
            return {'message': 'success', 'theme': selected_theme}, 200
        except SQLAlchemyError as e:
            print(e)
            return {"message": "Error"}
    return {"message": "Error"}

@blp.route("/apiv1/data/user/change_default_search", methods=['POST'])
def change_user_default_command():
    print('Request Incoming')
    jwt_token = request.json.get("jwt_token")
    new_search_id = request.json.get("search_id")

    payload = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
    user_sub = payload.json()

    if user_sub:
        user_model = UsersModel.query.filter_by(id=user_sub['sub']).first()


        user_model.default_search_id = new_search_id

        try:
            db.session.commit()
            return {"message": "Success"}, 200
        except SQLAlchemyError as e:
            print(e)
            return {"message": "Error"}
    return {"message": "Error"}

@blp.route("/apiv1/data/user", methods=['POST'])
def get_user():
    jwt_token = request.json.get("jwt")
    data = {}

    payload = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
    user_sub = payload.json()

    user_query_model = UsersModel.query.filter_by(id=user_sub['sub']).first()
    user_query = user_query_model.to_dict()

    data['user_info'] = {
        'user_id': user_sub['sub'],
        'default_search_id': user_query['default_search_id'],
        'user_theme': user_query['user_theme'],
        'user_email': {'email': user_sub['email']['address'],
        'is_email_valid': user_sub['email']['is_verified']}
        }

    user_permissions = []
    permissions_model = PermissionsModel.query.filter_by(user_id=user_sub['sub']).all()
    if permissions_model:
        for permission in permissions_model:
            permissions_dict = permission.to_dict()
            user_permissions.append(permissions_dict)
    data['user_permissions'] = user_permissions
    print(f"User Permissions = {data['user_permissions']}")

    user_commands = []
    for permission in data['user_permissions']:
        if permission['permission_name'] == "commands":
            # Retrieve all commands
            commands_model = CommandsModel.query.all()
            
            for command in commands_model:
                command_dict = command.to_dict()
                
                # Filter commands based on permission level
                if command_dict['permission_level'] is None or command_dict['permission_level'] >= permission['permission_level']:
                    user_commands.append(command_dict)
                else:
                    print(f"No permission to {command.prefix}")

    data['user_commands'] = user_commands

    sidebar_links = []
    added_urls = []
    for command in data['user_commands']:
        if command["category"] == "shortcut" and command["url"].startswith("/internal/") and command["url"] not in added_urls:
            sidebar_links.append({"href": command["url"], "text": command["prefix"].capitalize(), "data_tab": command["prefix"]})
            added_urls.append(command["url"])

    data['user_sidebar_links'] = sidebar_links

    user_search_commands = []
    added_urls = []

    for command in data['user_commands']:
        if "search" in command["category"]:
            if command["url"] in added_urls:
                for user_command in user_search_commands:
                    if user_command["id"] == command["id"]:
                        if len(command["prefix"]) > len(user_command["text"]):
                            user_command["text"] = command["prefix"].capitalize()
                        break
            else:
                user_search_commands.append({"id": command["id"], "text": command["prefix"].capitalize(), "prefix": command["prefix"]})
                added_urls.append(command["url"])

    data['user_search_commands'] = user_search_commands

    return jsonify(data)

@blp.route("/apiv1/data/user/search/history", methods=['POST'])
def get_user_search_history():
    data = request.json.get("data")
    user_sub = data['user_info']['user_id']
    user_history_query = RequestsModel.query.filter_by(user_id=user_sub).order_by(RequestsModel.id.desc()).all()

    user_history_query_structured = {user_sub: {}}
    for history_request in user_history_query:
        if history_request.is_search == True:
            try:
                user_query_url = history_request.command.search_url.format(history_request.encoded_query)
            except AttributeError:
                user_query_url = history_request.command.url
        elif history_request.is_search == False:
            user_query_url = history_request.command.url

        user_history_query_structured[user_sub][history_request.id] = {
            "request_id": history_request.id,
            "original_request": history_request.original_request,
            "query_url": user_query_url,
            "date_and_time": history_request.datetime_of_request
        }
    return user_history_query_structured

@blp.route("/apiv1/data/user/search/track", methods=['POST'])
def get_user_track_history():
    data = request.json.get("data")
    user_sub = data['user_info']['user_id']

    user_track_query = TrackingNumbersModel.query.filter_by(user_id=user_sub).order_by(TrackingNumbersModel.id.desc()).all()

    user_track_query_structured = {user_sub: {}}
    for track_request in user_track_query:
        tracking = get_tracking_number(track_request.tracking_number)
        user_track_query_structured[user_sub][track_request.id] = {
            "track_id": track_request.id,
            "tracking_number": track_request.tracking_number,
            "query_url": tracking.tracking_url,
            "courier_name": tracking.courier.name,
            "is_active": track_request.is_active,
            "note": track_request.note,
            "datetime_of_create_on_database": track_request.datetime_of_create_on_database
        }
    return user_track_query_structured

@blp.route('/apiv1/data/user/search/track/update_note', methods=['POST'])
def tracking_update_note():
    track_id = request.json.get('track_id')
    updated_note = request.json.get('updated_note')
    jwt_token = request.json.get("jwt_token")

    if updated_note.length() > 5000:
        return {"message": "Error"}

    payload = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
    user_sub = payload.json()

    if user_sub:
        selected_package = TrackingNumbersModel.query.filter_by(track_id=track_id).first()
        if selected_package.user_id == user_sub['sub']:
            selected_package.note = updated_note
            try:
                db.session.commit()
                return {'message': 'success'}, 200
            except SQLAlchemyError as e:
                print(e)
                return {"message": "Error"}
    return {"message": "Error"}

@blp.route("/apiv1/data/create_user", methods=['POST'])
def create_user():
    payload = request.json.get("payload")

    if payload:
        user_query = UsersModel.query.filter_by(id=payload['sub']).first()

    if not user_query:
        print("Creating user account.")
        create_user_for_internal(payload)

    if not BananaGameUserBananasModel.query.filter_by(id=payload['sub']).first():
        print("Creating game account.")
        create_user_banana_game_with_id(payload['sub'])


    return {"id": payload['sub']}