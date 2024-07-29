from flask import Blueprint, request, jsonify
from db import db
from sqlalchemy.exc import SQLAlchemyError

from models import CommandsModel, TrackingIdentificationModel

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