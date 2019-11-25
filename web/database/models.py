#models.py - Defines the database tables used in the website.
import datetime as dt
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
    verified = Column(db.Boolean, nullable=False)
    artpieces = relationship('ArtpieceModel', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<%r: %r>' % (self.id, self.email)

class EmailFailureState(Enum):
    submission_confirmation = 's_confirmation'
    bioart_completion = 'bioart_completion'

class EmailFailureModel(SurrogatePK, Model):
    __tablename__ = 'emailfailures'

    user_id = Column(db.Integer, db.ForeignKey('users.id'))
    artpiece_id = Column(db.Integer, db.ForeignKey('artpieces.id'))
    state = Column(db.Enum(EmailFailureState, values_callable=lambda x: [e.value for e in x])
            , nullable=False, name='failure_state')
    error_msg = Column(db.String(150), nullable=False)
