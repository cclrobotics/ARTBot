"""Database module, including the SQLAlchemy database object and DB-related utilities."""
from sqlalchemy.orm import relationship, deferred, composite
from enum import Enum

from web.extensions import db

# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship
deferred = deferred
composite = composite
Model = db.Model

# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` \
        to any declarative-mapped class.
    """

    __table_args__ = {'extend_existing': True}

    id = Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, (str, bytes)) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class OrderedEnum(Enum):
    @classmethod
    def _order(cls):
        return {item:num for num, item in enumerate(list(cls))}

    @property
    def _val_position(self):
        return self._order()[self]

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self._val_position >= other._val_position
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self._val_position > other._val_position
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self._val_position <= other._val_position
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self._val_position < other._val_position
        return NotImplemented
