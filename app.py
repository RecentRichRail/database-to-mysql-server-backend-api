import logging
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv

from db import db

from resources.login import blp as LoginBlueprint
from resources.settings import blp as SettingsBlueprint
from resources.commands import blp as CommandsBlueprint
from resources.search import blp as SearchBlueprint
from resources.user import blp as UserBlueprint
from resources.banana_game import blp as BananaGameBlueprint
from resources.devices import blp as DevicesBlueprint

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

app.register_blueprint(LoginBlueprint)
app.register_blueprint(SettingsBlueprint)
app.register_blueprint(CommandsBlueprint)
app.register_blueprint(SearchBlueprint)
app.register_blueprint(UserBlueprint)
app.register_blueprint(BananaGameBlueprint)
app.register_blueprint(DevicesBlueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=host_port, debug=True)