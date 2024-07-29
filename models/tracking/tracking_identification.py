from db import db

class TrackingIdentificationModel(db.Model):
    __tablename__ = "tracking_identification"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    prefix = db.Column(db.String(500), unique=True, nullable=False)
    url = db.Column(db.String(500))
    search_url = db.Column(db.String(500))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}