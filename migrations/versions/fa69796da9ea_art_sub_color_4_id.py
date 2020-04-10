"""art_sub_color_4_id

Revision ID: fa69796da9ea
Revises: 56c76cb1127d
Create Date: 2020-02-18 19:14:02.141440

"""
# revision identifiers, used by Alembic.
revision = 'fa69796da9ea'
down_revision = '56c76cb1127d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from migrations.utils.session import session_scope
from migrations.utils.image import (migrate_colors, extend_color_names_to_ids
        , replace_color_names)

Base = declarative_base()

class ArtpieceModel(Base):
    __tablename__ = 'artpieces'

    id = sa.Column(sa.Integer, primary_key=True)
    art = sa.Column(sa.JSON(), nullable=False, name='art_encoding')

class BacterialColorModel(Base):
    __tablename__ = 'bacterial_colors'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(20), unique=True, nullable=False)

def upgrade():
    with session_scope() as session:
        artpieces = session.query(ArtpieceModel).all()
        colors = session.query(BacterialColorModel).all()
        color_names_to_ids = {color.name: str(color.id) for color in colors}
        color_names_to_ids = extend_color_names_to_ids(color_names_to_ids)
        # replace art color names with ids
        for artpiece in artpieces:
            artpiece.art = migrate_colors(artpiece.art, color_names_to_ids)

def downgrade():
    with session_scope() as session:
        artpieces = session.query(ArtpieceModel).all()
        colors = session.query(BacterialColorModel).all()
        color_ids_to_names = {str(color.id): color.name for color in colors}
        color_ids_to_names = replace_color_names(color_ids_to_names)
        for artpiece in artpieces:
            artpiece.art = migrate_colors(artpiece.art, color_ids_to_names)
