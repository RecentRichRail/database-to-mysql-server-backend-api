from flask import Blueprint, request, current_app
import requests
from models import UsersModel, RequestsModel, PermissionsModel, CommandsModel
from db import db

# from models import CommandsModel, BananaGameUserBananasModel, BananaGameLifetimeBananasModel, BananaGameButtonPressModel

blp = Blueprint('admin', __name__)

# def get_user_info_and_auth(jwt_token):
#     data = {}

#     payload = requests.post(f"http://{current_app.authentication_server}/apiv1/auth/get_user_info", json={"jwt": jwt_token})
#     user_sub = payload.json()

#     user_query_model = UsersModel.query.filter_by(id=user_sub['sub']).first()
#     user_query = user_query_model.to_dict()

#     data['user_info'] = {'user_id': user_sub['sub'], 'default_search_id': user_query['default_search_id'],'user_email': {'email': user_sub['email']['address'], 'is_email_valid': user_sub['email']['is_verified']}}

#     permissions_model = PermissionsModel.query.filter_by(user_id=user_sub['sub']).all()
#     if permissions_model:
#         permissions = [permission.to_dict() for permission in permissions_model]
#         data['user_permissions'] = permissions

#     user_commands = []
#     for permission in data['user_permissions']:
#         if permission['permission_name'] == "commands":
#             # Retrieve all commands
#             commands_model = CommandsModel.query.all()
#             # commands_model = commands_model.to_dict()
            
#             for command in commands_model:
#                 command_dict = command.to_dict()
                
#                 # Filter commands based on permission level
#                 if command_dict['permission_level'] is None or command_dict['permission_level'] >= permission['permission_level']:
#                     user_commands.append(command_dict)
#                 else:
#                     print(f"No permission to {command.prefix}")

#     data['user_commands'] = user_commands
#     return data

@blp.route("/apiv1/admin/all_users", methods=['POST'])
def get_all_user_id():
    data = request.json.get("data")

    # data = get_user_info_and_auth(jwt_token)

    for permission in data['user_permissions']:
        if permission['permission_name'] == "admin" and permission['permission_level'] == 0:

            # user_query = UsersModel.query.filter_by(id=user_sub['sub']).first()
            admin_users_query = UsersModel.query.order_by(UsersModel.id.desc()).all()

            admin_user_query_structured = {}
            for user in admin_users_query:
                admin_user_query_structured[user.id] = user.to_dict()

            print(admin_user_query_structured)
            return admin_user_query_structured
    else:
        return {"message": "No permission for this resource."}

@blp.route("/apiv1/admin/user/search/history", methods=['POST'])
def get_user_search_history():
    data = request.json.get("data")
    selected_user = request.json.get("selected_user")

    # data = get_user_info_and_auth(jwt_token)

    for permission in data['user_permissions']:
        if permission['permission_name'] == "admin" and permission['permission_level'] == 0:

            # user_query = UsersModel.query.filter_by(id=user_sub['sub']).first()
            admin_history_query = RequestsModel.query.filter_by(user_id=selected_user).order_by(RequestsModel.id.desc()).all()

            admin_history_query_structured = {selected_user: {}}
            for history_request in admin_history_query:
                if history_request.is_search == True:
                    user_query_url = history_request.command.search_url.format(history_request.encoded_query)
                elif history_request.is_search == False:
                    user_query_url = history_request.command.url

                admin_history_query_structured[selected_user][history_request.id] = {
                    "request_id": history_request.id,
                    "original_request": history_request.original_request,
                    "query_url": user_query_url,
                    "date_and_time": history_request.datetime_of_request
                }

            # print(admin_history_query_structured)
            return admin_history_query_structured
    else:
        return {"message": "No permission for this resource."}