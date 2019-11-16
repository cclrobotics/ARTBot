"""Extensions module. Each extension is initialized in the app factory located in app.py."""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, Model
from flask_mail import Mail

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
        return self.save()

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
