import urllib.parse
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from models import UsersModel, CommandsModel, RequestsModel
from db import db

def run(data):

    user_query = data['user_query']
    print(user_query)
    user_info = data['user_info']

    user_query['search_query'] = user_query['original_request'].replace(user_query['prefix'], '', 1).strip()
    if user_query['search_query'] == "":
        user_query['search_query'] = None
        user_query['is_search'] = False

    user_query['search_query'] = user_query['original_request']
    user_query['encoded_query'] = urllib.parse.quote_plus(user_query['search_query'])
    user_query['is_search'] = True

    user_model = UsersModel.query.filter_by(id=user_info['user_id']).first()
    user_command_model = CommandsModel.query.filter_by(id=user_model.default_search_id).first()
    user_command = user_command_model.to_dict()

    if current_app.allow_logging:

        request_dict_format = {
            "original_request": user_query.get('original_request', "Error"),
            "user_id": user_info.get('user_id', "Error"),
            "prefix": user_query.get('prefix', "Error"),
            "search_query": user_query.get('search_query', "Error"),
            "encoded_query": user_query.get('encoded_query', "Error"),
            "is_search": user_query.get('is_search', "Error"),
            "command_id": user_command.get('id', "Error"),
            "datetime_of_request": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                }

        print("search_request data = ", request_dict_format)

        request_model = RequestsModel(**request_dict_format)

        try:
            db.session.add(request_model)
            db.session.commit()
            print("Search request recorded.")
        except SQLAlchemyError as e:
            print(e)
            print("Failed to record search request.")

    return {"funtion_triggered": True, "funtion_return": user_command['search_url'].format(user_query['encoded_query'])}