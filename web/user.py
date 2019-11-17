import datetime as dt
from web.database.models import (UserModel, ArtpieceModel, SubmissionStatus)
import web.artpiece as artpiece

Model = UserModel

class User():
    def __init__(self, model):
        self._model = model

    @classmethod
    def _create(cls, email, created_at, verified):
        return cls(Model(email=email, created_at=created_at, verified=verified).save())

    @classmethod
    def from_email(cls, email):
        return cls._create(email, dt.datetime.now(), False)

    @classmethod
    def get_by_email(cls, email):
        model = Model.query.filter(Model.email == email).one_or_none()
        return cls(model) if model else None

    @classmethod
    def get_by_id(cls, id):
        model = Model.get_by_id(id)
        return cls(model) if model else None

    def make_artpiece(self, title, art):
        return artpiece.make_artpiece(title, art, self._model.id).save()

    def has_active_submission(self):
        return self._model.artpieces.filter(
                ArtpieceModel.status == SubmissionStatus.submitted).count() > 0

    @property
    def email(self):
        return self._model.email
