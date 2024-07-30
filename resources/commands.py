from flask import Blueprint, request, jsonify
from db import db
from sqlalchemy.exc import SQLAlchemyError

from models import CommandsModel

blp = Blueprint('commands', __name__)

@blp.route("/apiv1/commands", methods=['GET'])
def get_commands():
    cmd_query = CommandsModel.query.all()
    commands = [command.to_dict() for command in cmd_query]
    return jsonify(commands)

@blp.route("/apiv1/commands/create_commands", methods=['POST'])
def create_commands():
    data = request.get_json()

    cmd_query = CommandsModel.query.filter_by(prefix=data['prefix']).first()
    if not cmd_query:
        command_model = CommandsModel(category=data['category'], prefix=data['prefix'], url=data['url'], search_url=data.get('search_url'))
        try:
            db.session.add(command_model)
            db.session.commit()
            return {"message": "Command created successfully"}
        except SQLAlchemyError as e:
            print(e)
    else:
        return {"message": "Command already exists"}

# May need to turn this into a "POST" request
# Thinking on having "Functions" - When a query is sent from the search it loops through funtions
# This will also allow a future UI editor - Create a funtion, the function gets added to codebase, funtion runs
# The actual search will need to be a funtion rather than the logic being done on the front-end
# When a function is not able to preform or is not going to be used will need to have an output the code will understand to go to the next function
# When the function is executed, It will only return a redirect link, that will be sent to the front end and will redirect the user
@blp.route("/apiv1/commands/<command_prefix>", methods=['GET'])
def get_command(command_prefix):

    cmd_query = CommandsModel.query.filter_by(prefix=command_prefix).first()
    if not cmd_query:
        track_query = TrackingIdentificationModel.query.all()
        for tracking in track_query:
            if tracking.prefix.upper() in command_prefix.upper():
                return_tracking = tracking.to_dict()
                return_tracking["category"] = "tracking"
                return return_tracking
        return {"message": "Command not found"}
    else:
        return cmd_query.to_dict()