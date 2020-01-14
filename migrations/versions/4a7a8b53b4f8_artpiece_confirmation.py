"""Artpiece confirmation

Revision ID: 4a7a8b53b4f8
Revises: 802864c6122e
Create Date: 2019-11-21 15:03:16.158623

"""

# revision identifiers, used by Alembic.
revision = '4a7a8b53b4f8'
down_revision = '802864c6122e'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ArtpieceModel(Base):
    __tablename__ = 'artpieces'

    id = sa.Column(sa.Integer, primary_key=True)
    confirmed = sa.Column(sa.Boolean, nullable=False)


def upgrade():
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    op.add_column('artpieces', sa.Column('confirmed', sa.Boolean, nullable=True))

    artpieces = session.query(ArtpieceModel).all()
    for artpiece in artpieces:
        artpiece.confirmed = True

    session.commit()

    op.alter_column('artpieces', 'confirmed', nullable=False)


def downgrade():
    op.drop_column('artpieces', 'confirmed')
