import urllib.parse
from flask import current_app
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from models import CommandsModel, RequestsModel
from db import db


def run(data):
    user_query = data['user_query']
    user_info = data['user_info']

    data['user_query']['search_query'] = data['user_query']['original_request'].replace(data['user_query']['prefix'], '', 1).strip()
    if data['user_query']['search_query'] == "":
        data['user_query']['search_query'] = None
        data['user_query']['is_search'] = False
    else:
        data['user_query']['is_search'] = True

    # print(data['user_commands'])

    shortcut_command = next((cmd for cmd in data['user_commands'] if cmd['prefix'] == user_query['prefix']), None)
    # shortcut_command_model = CommandsModel.query.filter_by(prefix=data['user_query']['prefix']).first()
    # if shortcut_command_model != None:
    if shortcut_command:
        if data['user_query']['is_search']:
            encoded_query = urllib.parse.quote_plus(user_query['search_query'])
            user_query['encoded_query'] = encoded_query
        else:
            user_query['encoded_query'] = None
    else:
        return {"function_triggered": False}
    
    print(data['user_query']['encoded_query'])

    request_dict_format = {
        "original_request": user_query['original_request'],
        "user_id": user_info['user_id'],
        "prefix": user_query['prefix'],
        "search_query": user_query['search_query'],
        "encoded_query": data['user_query']['encoded_query'],
        "is_search": user_query['is_search'],
        "command_id": shortcut_command['id'],
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
        # logging.info(f"redirecting to {shortcut_command['search_url'].format(data['user_query']['encoded_query'])}")
        return {"funtion_triggered": True, "funtion_return": shortcut_command['search_url'].format(data['user_query']['encoded_query'])}

    else:
        # logging.info(f"redirecting to {shortcut_command['url']}")
        return {"funtion_triggered": True, "funtion_return": shortcut_command['url']}