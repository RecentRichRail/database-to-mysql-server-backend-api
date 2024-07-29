from flask import Blueprint, request
from datetime import datetime, timezone

from db import db
from models import RequestsModel, TrackingNumbersModel
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint('search', __name__)

@blp.route("/apiv1/search/search_request", methods=['POST'])
def search_request():
    data = request.get_json()
    print(f"data recieved: {data}")

    request_dict = {
        "original_request": data.get('original_request', "Error"),
        "user_id": data.get('user_id', "Error"),
        "prefix": data.get('prefix', "Error"),
        "search_query": data.get('search_query', "Error"),
        "encoded_query": data.get('encoded_query', "Error"),
        "is_search": data.get('is_search', "Error"),
        "command_id": data.get('command_id', "Error"),
        "datetime_of_request": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            }

    print("search_request data = ", request_dict)

    request_model = RequestsModel(**request_dict)

    try:
        db.session.add(request_model)
        db.session.commit()
        print("Search request recorded.")
        return {"message": "Search request recorded."}
    except SQLAlchemyError as e:
        print(e)
        print("Failed to record search request.")
        return {"message": "Failed to record search request."}
    
@blp.route("/apiv1/search/track_request", methods=['POST'])
def track_request():
    data = request.get_json()
    print(f"data recieved: {data}")

    track_query = TrackingNumbersModel.query.filter_by(prefix=data['prefix'].upper()).first()
    if track_query:
        return {"message": "Track request previously recorded."}

    request_dict = {
        "user_id": data.get('user_id', "Error"),
        "tracking_number": data.get('prefix', "Error").upper(),
        "datetime_of_create_on_database": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            }

    print("track_request data = ", request_dict)

    request_model = TrackingNumbersModel(**request_dict)

    try:
        db.session.add(request_model)
        db.session.commit()
        print("Track request recorded.")
        return {"message": "Track request recorded."}
    except SQLAlchemyError as e:
        print(e)
        print("Failed to record search request.")
        return {"message": "Failed to record track request."}