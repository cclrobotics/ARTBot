import datetime as dt
from web.database.models import (UserModel, UserRole, ArtpieceModel, SubmissionStatus)


_Model = UserModel

class User():
    def __init__(self, model):
        self._model = model

    @classmethod
    def _create(cls, email, created_at, role):
        return cls(_Model(email=email, created_at=created_at, role=role).save())

    @classmethod
    def from_email(cls, email):
        return cls._create(email, dt.datetime.now(), list(UserRole)[0])

    @classmethod
    def get_by_email(cls, email):
        model = _Model.query.filter(_Model.email == email).one_or_none()
        return cls(model) if model else None

    @classmethod
    def get_by_id(cls, id):
        model = _Model.get_by_id(id)
        return cls(model) if model else None

    def create_artpiece(self, title, art):
        from .artpiece import Artpiece
        return Artpiece.create(self._model.id, title, art)

    def has_active_submission(self):
        return self._model.artpieces.filter(
                ArtpieceModel.status == SubmissionStatus.submitted).count() > 0

    @property
    def email(self):
        return self._model.email

    @property
    def role(self):
        return self._model.role
