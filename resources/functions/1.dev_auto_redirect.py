from flask import current_app
import requests

def run(data):
    if data["user_active_env"] != "dev":
        for permission in data['user_permissions']:
            if permission['permission_name'] == "dev" and permission['permission_level'] <= 999:
                response = requests.get(f"{current_app.dev_server}/external/status")
                dev_server_status = response.json()

                if dev_server_status == None:
                    return {"function_triggered": False}
                
                elif dev_server_status['status'] == 200:
                    dev_user_query = data['user_query']['original_request']
                    return {"funtion_triggered": True, "funtion_return": f"https://dev.spicerhome.net/internal/search?q={dev_user_query}"}
            
    return {"function_triggered": False}