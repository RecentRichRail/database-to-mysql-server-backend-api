from db import db

class BananaGameLifetimeBananasModel(db.Model):
    __tablename__ = "banana_game_user_bananas_lifetime"

    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    lifetime_bananas = db.Column(db.Integer, default=0, unique=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}