from flask import Blueprint, request, jsonify
import os, importlib.util

from db import db

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
                    return jsonify({"internal_search": script_return.get("internal_search", False), "function_data": script_return['funtion_return']})
            except Exception as e:
                print(f"Error running {filename}: {e}")
                return jsonify({"error": str(e)}), 500
            
    print(f"Running 'search.py'")
    script_path = os.path.join('resources/functions', 'search.py')
    try:
        script_return = run_funtion(script_path, data)
        # print(f"script_return: {script_return}")
        if script_return.get("funtion_triggered"):
            return jsonify({"internal_search": script_return.get("internal_search", False), "function_data": script_return['funtion_return']})
    except Exception as e:
                print(f"Error running search.py: {e}")
                return jsonify({"error": str(e)}), 500
    # print({"redirect_url": run_funtion(os.path.join('resources/functions', 'search.py'), data)['funtion_return']})
    return jsonify({"internal_search": script_return.get("internal_search", False), "function_data": run_funtion(os.path.join('resources/functions', 'search.py'), data)['funtion_return']})