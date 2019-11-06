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
    email = Column(db.String(50), nullable=False)
    submit_date = Column(db.DateTime(), nullable=False)
    art = Column(db.JSON(), nullable=False, name='art_encoding')
    status = Column(
            db.Enum(SubmissionStatus, values_callable=lambda x: [e.value for e in x])
            , nullable=False, name='submission_status')
    raw_image = deferred(Column(db.LargeBinary(), nullable=False))

    def __repr__(self):
        return '<%r: %r>' % (self.id, self.title)
