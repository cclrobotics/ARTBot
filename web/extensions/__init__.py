"""Extensions module. Each extension is initialized in the app factory located in app.py."""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, Model
from flask_mail import Mail
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from .argon2_config import Argon2
from .jwt_config import user_lookup_callback

class CRUDMixin(Model):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it to the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=False, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save(commit=commit)

    def save(self, commit=False):
        """Save the record."""
        db.session.add(self)
        db.session.flush()
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=False):
        """Remove the record from the database."""
        db.session.delete(self)
        db.session.flush()
        return commit and db.session.commit()

db = SQLAlchemy(model_class=CRUDMixin)
migrate = Migrate()
mail = Mail()
cache = Cache()
jwt = JWTManager()
argon2 = Argon2()

jwt.user_lookup_loader(user_lookup_callback)