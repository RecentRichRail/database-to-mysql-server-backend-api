from flask import Blueprint, request, current_app
from models import UsersModel, RequestsModel
from db import db

blp = Blueprint('admin', __name__)

@blp.route("/apiv1/admin/all_users", methods=['POST'])
def get_all_user_id():
    data = request.json.get("data")

    for permission in data['user_permissions']:
        if permission['permission_name'] == "admin" and permission['permission_level'] == 0:

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

    for permission in data['user_permissions']:
        if permission['permission_name'] == "admin" and permission['permission_level'] == 0:

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
            return admin_history_query_structured
    else:
        return {"message": "No permission for this resource."}