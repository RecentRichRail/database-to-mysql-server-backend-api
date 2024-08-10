import urllib.parse
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import requests

from models import UsersModel, CommandsModel, RequestsModel
from db import db

def run(data):

    user_query = data['user_query']
    user_offset = data['user_query']['offset']
    # print(user_query)
    user_info = data['user_info']

    user_query['search_query'] = user_query['original_request'].replace(user_query['prefix'], '', 1).strip()
    if user_query['search_query'] == "":
        user_query['search_query'] = None
        user_query['is_search'] = False

    user_query['search_query'] = user_query['original_request']
    user_query_original_request = user_query['original_request']
    user_query['encoded_query'] = urllib.parse.quote_plus(user_query['search_query'])
    user_query['is_search'] = True

    user_command_model = CommandsModel.query.filter_by(id=user_info['default_search_id']).first()
    user_command = user_command_model.to_dict()

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
    
    # if user_command['url'] != "/internal/search":
    #     return {"funtion_triggered": True, "funtion_return": user_command['search_url'].format(user_query['encoded_query'])}
    
    else:
        # for permission in data['user_permissions']:
        #     if permission['permission_name'] == "commands" and permission['permission_level'] <= 50:
        base_url = "https://api.search.brave.com/res/v1/"
        endpoint = "web"
        url = base_url + endpoint + "/search"
        headers = {"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": current_app.BRAVE_API_KEY}

        params = {"q": user_query_original_request,"country": "US","search_lang": "en","ui_lang": "en-US","count": 20,"offset": user_offset,"safesearch": "strict","freshness": None,"text_decorations": None,"spellcheck": True,"result_filter": "web","goggles_id": None,"units": None,"extra_snippets": None}
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(url, headers=headers, params=params)
        search_results = response.json()


        # search_results = Brave().search(q=user_query, count=20, offset=user_offset)
        # print(search_results)
        return {"funtion_triggered": True, "internal_search": True, "funtion_return": search_results}

            # else:
            #     return {"funtion_triggered": True, "funtion_return": f"/internal/search?q=b {user_query_original_request}"}
        # pass