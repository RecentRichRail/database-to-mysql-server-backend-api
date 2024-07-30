import urllib.parse
from flask import Blueprint, current_app, redirect, request, render_template
import requests
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from models import UsersModel, CommandsModel, RequestsModel
from db import db

def run(data):
    # This will only run when no other functions are triggered
    # This is default search only, for "yt rick roll" use shortcut
    # return {"funtion_triggered": True, "funtion_return": "https://google.com"}

    request_dict = {'original_request': data['user_query']}
    request_dict['user_id'] = data['user_id']

    # Check if first word in command is in prefixes
    request_dict['prefix'] = data['user_query'].split(' ')[0].lower()
    logging.info(f"'{request_dict['prefix']}' has been set as the prefix")
    request_dict['search_query'] = data['user_query'].replace(request_dict['prefix'], '', 1).strip()
    if request_dict['search_query'] == "":
        request_dict['search_query'] = None
        request_dict['is_search'] = False

    # temp_prefix_for_api_call = request_dict['prefix']
    # cmd_query = CommandsModel.query.filter_by(prefix=request_dict['prefix']).first()
    # print(f"Return from API: {cmd_query}")
    # if cmd_query != {"message": "Command not found"}:
    #     return {"funtion_triggered": False}
    

    request_dict['search_query'] = request_dict['original_request']
    logging.info(f"'{request_dict['search_query']}' has been set as the search_query")
    request_dict['encoded_query'] = urllib.parse.quote_plus(request_dict['search_query'])
    logging.info(f"'{request_dict['encoded_query']}' has been set as the encoded_query")
    request_dict['is_search'] = True
    logging.info(f"'{request_dict['is_search']}' has been set as the is_search")

    user_query = UsersModel.query.filter_by(id=request_dict['user_id']).first()
    cmd_query = CommandsModel.query.filter_by(id=user_query.default_search_id).first()
    cmd_query = cmd_query.to_dict()
    print(cmd_query)
    request_dict['command_id'] = cmd_query['id']
    command_dict = {'category': cmd_query['category']}
    command_dict['id'] = cmd_query['id']
    command_dict['url'] = cmd_query['url']
    command_dict['search_url'] = cmd_query['search_url']
    command_dict['prefix'] = cmd_query['prefix']

    if current_app.allow_logging:
        print(f"Passing data: {request_dict}")
        # requests.post(f"http://{current_app.mysql_database_api}/apiv1/search/search_request", json=request_dict)
        # data = request.get_json()
        print(f"data recieved: {request_dict}")

        request_dict_format = {
            "original_request": request_dict.get('original_request', "Error"),
            "user_id": request_dict.get('user_id', "Error"),
            "prefix": request_dict.get('prefix', "Error"),
            "search_query": request_dict.get('search_query', "Error"),
            "encoded_query": request_dict.get('encoded_query', "Error"),
            "is_search": request_dict.get('is_search', "Error"),
            "command_id": request_dict.get('command_id', "Error"),
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

    if request_dict['is_search']:
        logging.info(f"'request_dict['is_search']' is True")
        logging.info(f"redirecting to {command_dict['search_url'].format(request_dict['encoded_query'])}")
        return {"funtion_triggered": True, "funtion_return": command_dict['search_url'].format(request_dict['encoded_query'])}

    else:
        logging.info(f"'request.is_search' is False")
        logging.info(f"redirecting to {command_dict['url']}")
        return {"funtion_triggered": True, "funtion_return": command_dict['url']}