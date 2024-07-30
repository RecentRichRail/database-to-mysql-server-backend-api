from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import os, importlib.util

from db import db
from models import RequestsModel, TrackingNumbersModel
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint('search', __name__)

def run_funtion(script_path, data):
    spec = importlib.util.spec_from_file_location("module.name", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run(data)

# May need to turn this into a "POST" request
# Thinking on having "Functions" - When a query is sent from the search it loops through funtions
# This will also allow a future UI editor - Create a funtion, the function gets added to codebase, funtion runs
# The actual search will need to be a funtion rather than the logic being done on the front-end
# When a function is not able to preform or is not going to be used will need to have an output the code will understand to go to the next function
# When the function is executed, It will only return a redirect link, that will be sent to the front end and will redirect the user
@blp.route("/apiv1/search/query", methods=['POST'])
def user_search_query():
    data = request.get_json()
    print(f"Data received: {data}")

    data['user_query']['prefix'] = data['user_query']['original_request'].split(' ')[0].lower()

    # Should be how the data looks:
    # data = {'user_query': {'prefix': 'yellow', 'original_request': 'yellow cab'}, 'user_info': {'user_id': 'ID12345'}}
    # After tracking.py:
    # data = {'user_query': {'original_request': 'yellow cab', 'prefix': 'yellow'}, 'user_info': {'user_id': 'ID12345'}, 'tracking_details': None}

    for filename in os.listdir('resources/functions'):
        if filename.endswith('.py') and filename != 'search.py':
            print(f"Running {filename}")
            script_path = os.path.join('resources/functions', filename)
            try:
                script_return = run_funtion(script_path, data)
                if script_return.get("funtion_triggered"):
                    return jsonify({"redirect_url": script_return['funtion_return']})
            except Exception as e:
                print(f"Error running {filename}: {e}")
                return jsonify({"error": str(e)}), 500
            
    print(f"Running 'search.py'")
    print({"redirect_url": run_funtion(os.path.join('resources/functions', 'search.py'), data)['funtion_return']})
    return jsonify({"redirect_url": run_funtion(os.path.join('resources/functions', 'search.py'), data)['funtion_return']})

# No longer needed, This function is now nested in with the function
# @blp.route("/apiv1/search/search_request", methods=['POST'])
# def search_request():
#     data = request.get_json()
#     print(f"data recieved: {data}")

#     request_dict = {
#         "original_request": data.get('original_request', "Error"),
#         "user_id": data.get('user_id', "Error"),
#         "prefix": data.get('prefix', "Error"),
#         "search_query": data.get('search_query', "Error"),
#         "encoded_query": data.get('encoded_query', "Error"),
#         "is_search": data.get('is_search', "Error"),
#         "command_id": data.get('command_id', "Error"),
#         "datetime_of_request": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
#             }

#     print("search_request data = ", request_dict)

#     request_model = RequestsModel(**request_dict)

#     try:
#         db.session.add(request_model)
#         db.session.commit()
#         print("Search request recorded.")
#         return {"message": "Search request recorded."}
#     except SQLAlchemyError as e:
#         print(e)
#         print("Failed to record search request.")
#         return {"message": "Failed to record search request."}
    
# @blp.route("/apiv1/search/track_request", methods=['POST'])
# def track_request():
#     data = request.get_json()
#     print(f"data recieved: {data}")

#     track_query = TrackingNumbersModel.query.filter_by(tracking_number=data['prefix'].upper()).first()
#     if track_query:
#         return {"message": "Track request previously recorded."}

#     request_dict = {
#         "user_id": data.get('user_id', "Error"),
#         "tracking_number": data.get('prefix', "Error").upper(),
#         "datetime_of_create_on_database": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
#             }

#     print("track_request data = ", request_dict)

#     request_model = TrackingNumbersModel(**request_dict)

#     try:
#         db.session.add(request_model)
#         db.session.commit()
#         print("Track request recorded.")
#         return {"message": "Track request recorded."}
#     except SQLAlchemyError as e:
#         print(e)
#         print("Failed to record search request.")
#         return {"message": "Failed to record track request."}