import datetime as dt
from web.database.models import (UserModel, UserRole, ArtpieceModel, SubmissionStatus)

#TODO add a hasher: from web.extensions import argon2

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
    
    def set_password(self, password):
        self._model.password_hash = password #TODO set to hash: argon2.password_hasher.hash(password)

    def is_password_valid(self, password):
        try:
            if self.password_hash != password: raise Exception #TODO implement hashing: argon2.password_hasher.verify(self.password_hash, password)
        except: #argon2.exceptions.VerificationError:
            return False;
        return True
    
    @property
    def password_hash(self):
        return self._model.password_hash
   
    @property
    def id(self):
        return self._model.id
    
    @property
    def email(self):
        return self._model.email

    @property
    def role(self):
        return self._model.role
