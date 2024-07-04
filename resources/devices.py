from flask import Blueprint, request, jsonify, current_app
import requests, hmac
# from models import 
from db import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from models import DevicesSerialNumberModel, DevicesLastCheckInModel, DevicesNetworkModel

blp = Blueprint('devices', __name__)

@blp.route("/apiv1/devices/send_command", methods=['POST'])
def send_command():
    # It can be a command that is added to the database, When the device checks in, it will get the command and execute it.
    # This also needs to verify the source of the command. We can use the JWT token for this.
    # If the user of the JWT token is an admin, then they can send commands.
    # These commands need to be logged with IP, User ID, Permission Level, Command, Device, and Time.
    # Only the most recent command will be executed. The rest need to be logged and ignored.
    # If there is a power on command then this needs to send a WOL packet to the device.
    return {"message": "Send command not available at this time."}

@blp.route("/apiv1/devices/check_in", methods=['POST'])
def check_in():
    # Needs to return either action or last check in time.
    # Check in needs the serial number and the unique identifier verification key, and IP address.
    return {"message": "Check in not available at this time."}

@blp.route("/apiv1/devices/create_device", methods=['POST'])
def create_device():
    serial_number = request.json.get("serial_number")
    public_verification_key = request.json.get("public_verification_key")
    if not hmac.compare_digest(public_verification_key, current_app.public_verification_key):
        return jsonify({"error": "Unable to verify source."})
    unique_identifier_verification_key = request.json.get("unique_identifier_verification_key")
    ip_address = request.json.get("ip_address")

    serial_number_exists = DevicesSerialNumberModel.query.filter_by(serial_number=serial_number).first()

    if not serial_number_exists:
        print("Creating device.")

        device_information = {"serial_number": serial_number,
            "unique_identifier_verification_key": unique_identifier_verification_key}
        
        db.session.add(DevicesSerialNumberModel(**device_information))

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)

        DeviceQuery = DevicesSerialNumberModel.query.filter_by(serial_number=serial_number).first()
        
        device_information_last_check_in = {"id": DeviceQuery.id}
        
        device_information_network = {"id": DeviceQuery.id,
            "ip_address": ip_address}
        
        db.session.add(DevicesLastCheckInModel(**device_information_last_check_in))
        db.session.add(DevicesNetworkModel(**device_information_network))

        try:
            db.session.commit()
            return {"id": DeviceQuery.id, "serial_number": DeviceQuery.serial_number, "ip_address": ip_address}
        except SQLAlchemyError as e:
            print(e)

    return {"message": "Device already exists."}