import datetime as dt
from web.database.models import (UserModel, ArtpieceModel, SubmissionStatus)
import web.artpiece as artpiece

Model = UserModel

class User():
    def __init__(self, model):
        self.model = model

    @classmethod
    def _create(cls, email, created_at, verified):
        return cls(Model(email=email, created_at=created_at, verified=verified).save())

    @classmethod
    def from_email(cls, email):
        return cls._create(email, dt.datetime.now(), False)

    @classmethod
    def get_by_email(cls, email):
        model = Model.query.filter(Model.email == email).one_or_none()
        if not model:
            return None
        return cls(model)

    def make_artpiece(self, title, art):
        return artpiece.make_artpiece(title, art, self.model.id).save()

    def has_active_submission(self):
        return self.model.artpieces.filter(
                ArtpieceModel.status == SubmissionStatus.submitted).count() > 0

    @property
    def email(self):
        return self.model.email
