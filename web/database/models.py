#models.py - Defines the database tables used in the website.
import datetime as dt
from collections import namedtuple
from enum import Enum
from .database import (Model, SurrogatePK, db, Column,
                              reference_col, relationship, deferred, composite)

class SubmissionStatus(Enum):
    submitted = 'Submitted'
    processing = 'Processing'
    processed = 'Processed'

#Stores all submitted art and allows it to be referenced later by the robot interface
class ArtpieceModel(SurrogatePK, Model):
    __tablename__ = 'artpieces'

    slug = Column(db.String(60), nullable=False, unique=True, index=True)
    title = Column(db.String(50), nullable=False)
    user_id = Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    submit_date = Column(db.DateTime(), nullable=False)
    art = Column(db.JSON(), nullable=False, name='art_encoding')
    status = Column(
            db.Enum(SubmissionStatus, values_callable=lambda x: [e.value for e in x])
            , nullable=False, name='submission_status')
    confirmed = Column(db.Boolean, nullable=False)
    raw_image = deferred(Column(db.LargeBinary(), nullable=False))

    def __repr__(self):
        return '<%r: %r>' % (self.id, self.title)

class UserModel(SurrogatePK, Model):
    __tablename__ = 'users'

    email = Column(db.String(50), nullable=False, index=True, unique=True)
    created_at = Column(db.DateTime(), nullable=False)
    artpieces = relationship('ArtpieceModel', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<%r: %r>' % (self.id, self.email)

RGBA = namedtuple('RGBA', ['r','g','b','a'])

class BacterialColorModel(SurrogatePK, Model):
    __tablename__ = 'bacterial_colors'

    name = Column(db.String(20), unique=True, nullable=False)
    red = Column(db.SmallInteger(), nullable=False)
    green = Column(db.SmallInteger(), nullable=False)
    blue = Column(db.SmallInteger(), nullable=False)
    opacity = Column(db.SmallInteger(), nullable=False)
    biobrick_id = Column(db.String(30), nullable=False)
    in_use = Column(db.Boolean(), nullable=False)

    rgba = composite(RGBA, red, green, blue, opacity)

    def __repr__(self):
        return '<%r: (%r,%r,%r,%r)>' % (self.name, self.red, self.green, self.blue, self.opacity)

class EmailFailureState(Enum):
    submission_confirmation = 's_confirmation'
    bioart_completion = 'bioart_completion'

class EmailFailureModel(SurrogatePK, Model):
    __tablename__ = 'emailfailures'

    artpiece_id = Column(db.Integer, db.ForeignKey('artpieces.id'), nullable=False)
    state = Column(db.Enum(EmailFailureState, values_callable=lambda x: [e.value for e in x])
            , nullable=False, name='failure_state')
    error_msg = Column(db.String(150), nullable=False)
