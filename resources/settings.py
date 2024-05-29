from flask import Blueprint
from models import CommandsModel

blp = Blueprint('settings', __name__)

@blp.route("/apiv1/settings/default_search", methods=['GET'])
def get_default_search():
    cmd_query = CommandsModel.query.filter_by(category="default_search").first()
    print(cmd_query.to_dict())
    return {"default_search": cmd_query.to_dict()}