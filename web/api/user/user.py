import datetime as dt
from web.database.models import (UserModel, UserRole,
                                 SuperUserModel, SuperUserRole,
                                 ArtpieceModel, SubmissionStatus)
from web.extensions import argon2

class MetaUser():
    def __init__(self, model):
        self._model = model

    @classmethod
    def _Model(cls):
        try:
            return cls._get_model()
        except AttributeError:
            raise TypeError('MetaUser class is not meant to be accessed directly')

    @classmethod
    def _create(cls, email, created_at, role):
        _Model = cls._Model()
        return cls(_Model(email=email, created_at=created_at, role=role).save())

    @classmethod
    def from_email(cls, email):
        return cls._create(email, dt.datetime.now(), cls._default_role())

    @classmethod
    def get_by_email(cls, email):
        _Model = cls._Model()
        model = _Model.query.filter(_Model.email == email).one_or_none()
        return cls(model) if model else None

    @classmethod
    def get_by_id(cls, id):
        _Model = cls._Model()
        model = _Model.get_by_id(id)
        return cls(model) if model else None

    def set_password(self, password):
        self._model.password_hash = argon2.password_hasher.hash(password)

    def is_password_valid(self, password):
        try:
            argon2.password_hasher.verify(self.password_hash, password)
        except argon2.exceptions.VerificationError:
            return False
        except argon2.exceptions.InvalidHash:
            return False
        return True

    def password_needs_rehash(self):
        return argon2.password_hasher.check_needs_rehash(self.password_hash)
    
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


_Model = UserModel

class User(MetaUser):
    @classmethod
    def _get_model(cls):
        return UserModel
    @classmethod
    def _default_role(cls):
        return list(UserRole)[0]

    def create_artpiece(self, title, art):
        from .artpiece import Artpiece
        return Artpiece.create(self._model.id, title, art)

    def has_active_submission(self):
        return self._model.artpieces.filter(
                ArtpieceModel.status == SubmissionStatus.submitted).count() > 0
    

class SuperUser(MetaUser):
    @classmethod
    def _get_model(cls):
        return SuperUserModel
    @classmethod
    def _default_role(cls):
        return list(SuperUserRole)[0]