from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from tracking_numbers import get_tracking_number

from models import TrackingNumbersModel
from db import db

def run(data):

    data['tracking_details'] = get_tracking_number(data['user_query']['prefix'].upper())
    # print(f"Tracking.py data - {data}")
    if data['tracking_details'] == None:
        return {"funtion_triggered": False}


    # => TrackingNumber(
    #       valid=False,
    #       number='1ZY0X1930320121606',
    #       serial_number=[6, 0, 5, 1, 9, 3, 0, 3, 2, 0, 1, 2, 1, 6, 0],
    #       tracking_url='https://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=1ZY0X1930320121604',
    #       courier=Courier(code='ups', name='UPS'),
    #       product=Product(name='UPS'),
    #    )



    track_query = TrackingNumbersModel.query.filter_by(tracking_number=data['tracking_details'].number).first()
    if track_query:
        print({"message": "Track request previously recorded."})
        return {"funtion_triggered": True, "funtion_return": "/internal/search/track"}

    else:

        request_dict = {
            "user_id": data['user_info'].get('user_id', "Error"),
            "tracking_number": data['user_query'].get('prefix', "Error").upper(),
            "datetime_of_create_on_database": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                }

        print("track_request data = ", request_dict)

        request_model = TrackingNumbersModel(**request_dict)

        try:
            db.session.add(request_model)
            db.session.commit()
            print("Track request recorded.")
            return {"funtion_triggered": True, "funtion_return": "/internal/search/track"}
        except SQLAlchemyError as e:
            print(e)
            print("Failed to record search request.")
            return {"funtion_triggered": True, "funtion_return": "/internal/search/track"}