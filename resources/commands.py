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