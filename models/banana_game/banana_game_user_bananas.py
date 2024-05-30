from db import db

class BananaGameUserBananasModel(db.Model):
    __tablename__ = "banana_game_user_bananas"

    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    bananas = db.Column(db.Integer, default=0, unique=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}