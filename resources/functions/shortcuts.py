import urllib.parse
from flask import current_app
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from models import CommandsModel, RequestsModel
from db import db


def run(data):
    data['user_query']['search_query'] = data['user_query']['original_request'].replace(data['user_query']['prefix'], '', 1).strip()
    if data['user_query']['search_query'] == "":
        data['user_query']['search_query'] = None
        data['user_query']['is_search'] = False

    shortcut_command_model = CommandsModel.query.filter_by(prefix=data['user_query']['prefix']).first()
    if shortcut_command_model != None:
        shortcut_command = shortcut_command_model.to_dict()
        if data['user_query']['search_query']:
            data['user_query']['encoded_query'] = urllib.parse.quote_plus(data['user_query']['search_query'])
            if shortcut_command['category'] == "search":
                data['user_query']['is_search'] = True
    else:
        return {"funtion_triggered": False}

    if current_app.allow_logging:

        request_dict_format = {
            "original_request": data['user_query'].get('original_request', "Error"),
            "user_id": data['user_info'].get('user_id', "Error"),
            "prefix": data['user_query'].get('prefix', "Error"),
            "search_query": data['user_query'].get('search_query', "Error"),
            "encoded_query": data['user_query'].get('encoded_query', "Error"),
            "is_search": data['user_query'].get('is_search', "Error"),
            "command_id": shortcut_command.get('id', "Error"),
            "datetime_of_request": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                }

        print("search_request data = ", request_dict_format)

        request_model = RequestsModel(**request_dict_format)

        try:
            db.session.add(request_model)
            db.session.commit()
            print("Search request recorded.")
            print({"message": "Search request recorded."})
        except SQLAlchemyError as e:
            print(e)
            print("Failed to record search request.")
            print({"message": "Failed to record search request."})

    if data['user_query']['is_search']:
        logging.info(f"redirecting to {shortcut_command['search_url'].format(data['user_query']['encoded_query'])}")
        return {"funtion_triggered": True, "funtion_return": shortcut_command['search_url'].format(data['user_query']['encoded_query'])}

    else:
        logging.info(f"redirecting to {shortcut_command['url']}")
        return {"funtion_triggered": True, "funtion_return": shortcut_command['url']}