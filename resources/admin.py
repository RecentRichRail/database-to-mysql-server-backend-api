from flask import Blueprint, request, current_app
from models import UsersModel, RequestsModel, TrackingNumbersModel
from db import db

from tracking_numbers import get_tracking_number

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

@blp.route("/apiv1/admin/user/track/history", methods=['POST'])
def get_user_tracking_history():
    data = request.json.get("data")
    selected_user = request.json.get("selected_user")

    for permission in data['user_permissions']:
        if permission['permission_name'] == "admin" and permission['permission_level'] == 0:

            user_track_query = TrackingNumbersModel.query.filter_by(user_id=selected_user).order_by(TrackingNumbersModel.id.desc()).all()

            user_track_query_structured = {selected_user: {}}
            for track_request in user_track_query:
                tracking = get_tracking_number(track_request.tracking_number)
                user_track_query_structured[selected_user][track_request.id] = {
                    "track_id": track_request.id,
                    "tracking_number": track_request.tracking_number,
                    "query_url": tracking.tracking_url,
                    "courier_name": tracking.courier.name,
                    "is_active": track_request.is_active,
                    "datetime_of_create_on_database": track_request.datetime_of_create_on_database
                }
            return user_track_query_structured
    else:
        return {"message": "No permission for this resource."}