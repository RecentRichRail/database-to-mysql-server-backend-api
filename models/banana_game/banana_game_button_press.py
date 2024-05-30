from db import db
from datetime import datetime

class BananaGameButtonPressModel(db.Model):
    __tablename__ = "banana_game_button_press"

    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    button_clicks = db.Column(db.Integer, default=0, unique=False)
    bananas_per_button_click = db.Column(db.Integer, default=1, unique=False)
    datetime_of_last_button_press = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.now().strftime('%Y%m%d%H%M%S'))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}