import logging
from flask import Flask
import os
import json
from dotenv import load_dotenv

from db import db
import resources

from models import CommandsModel, PermissionsModel

from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

short_session_cookie_name = os.environ.get('short_session_cookie_name')
host_port = os.environ.get('host_port')
app.authentication_server = os.environ.get('authentication_server')
app.mysql_database_api = os.environ.get('mysql_database_api')
app.allow_logging = os.environ.get('allow_logging')
app.public_verification_key = os.environ.get('public_verification_key')

app.config["SQLALCHEMY_DB_HOST"] = os.environ.get('SQLALCHEMY_DB_HOST')
app.config["SQLALCHEMY_DB_USER"] = os.environ.get('SQLALCHEMY_DB_USER')
app.config["SQLALCHEMY_DB_PASSWORD"] = os.environ.get('SQLALCHEMY_DB_PASSWORD')
app.config["SQLALCHEMY_DB_NAME"] = os.environ.get('SQLALCHEMY_DB_NAME')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

if app.config["SQLALCHEMY_DB_HOST"] == 'sqlite':
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{app.config['SQLALCHEMY_DB_USER']}:{app.config['SQLALCHEMY_DB_PASSWORD']}@{app.config['SQLALCHEMY_DB_HOST']}/{app.config['SQLALCHEMY_DB_NAME']}"
    
db.init_app(app)
with app.app_context():
    db.create_all()
    print("Creating database.")

    try:
        with open('src/commands.json', 'r') as file:
            commands_data = json.load(file)
            logging.error(f"commands.json file was loaded.")
    except FileNotFoundError:
        logging.error(f"{os.system('pwd')} - Could not find commands.json file.")
        commands_data = {'commands': []}

    # for single_permission in commands_data['permissons']:
    #     for single_command_single_prefix in single_command['prefix']:
    #         command_for_data = single_command
    #         command_for_data['prefix'] = single_command_single_prefix
    #         cmd_query = CommandsModel.query.filter_by(prefix=command_for_data['prefix']).first()
    #         if not cmd_query:
    #             command_model = CommandsModel(category=command_for_data['category'], prefix=command_for_data['prefix'], url=command_for_data['url'], search_url=command_for_data.get('search_url'))
    #             try:
    #                 db.session.add(command_model)
    #                 db.session.commit()
    #                 print("Command created successfully")
    #             except SQLAlchemyError as e:
    #                 print(e)
    #         else:
    #             print("Command already exists")

    for single_command in commands_data['commands']:
        for single_command_single_prefix in single_command['prefix']:
            command_for_data = single_command
            command_for_data['prefix'] = single_command_single_prefix
            cmd_query = CommandsModel.query.filter_by(prefix=command_for_data['prefix']).first()
            command_model = CommandsModel(category=command_for_data['category'], prefix=command_for_data['prefix'], url=command_for_data['url'], search_url=command_for_data.get('search_url'), permission_level=command_for_data.get('permission_level'))
            if not cmd_query:
                try:
                    if not cmd_query:
                        db.session.add(command_model)
                        db.session.commit()
                        print("Command created successfully")
                except SQLAlchemyError as e:
                    print(e)
            else:
                print("Command already exists")

app.register_blueprint(resources.LoginBlueprint)
app.register_blueprint(resources.SettingsBlueprint)
app.register_blueprint(resources.CommandsBlueprint)
app.register_blueprint(resources.SearchBlueprint)
app.register_blueprint(resources.UserBlueprint)
app.register_blueprint(resources.AdminBlueprint)
app.register_blueprint(resources.BananaGameBlueprint)
app.register_blueprint(resources.DevicesBlueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=host_port, debug=True)