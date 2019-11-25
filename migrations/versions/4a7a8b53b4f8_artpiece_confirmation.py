"""Artpiece confirmation

Revision ID: 4a7a8b53b4f8
Revises: 802864c6122e
Create Date: 2019-11-21 15:03:16.158623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a7a8b53b4f8'
down_revision = '802864c6122e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('new_artpieces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column('submit_date', sa.DateTime(), nullable=False),
        sa.Column('art_encoding', sa.JSON(), nullable=False),
        sa.Column('submission_status'
        , sa.Enum('Submitted', 'Processing', 'Processed', name='submissionstatus')
        , nullable=False),
        sa.Column('raw_image', sa.LargeBinary(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('confirmed', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute(("INSERT INTO "
        "new_artpieces("
        "id, title, submit_date, art_encoding, submission_status, raw_image, user_id, confirmed) "
        "SELECT id, title, submit_date, art_encoding, submission_status, raw_image, user_id, True as confirmed "
        "FROM artpieces ")
    )
    op.drop_table('artpieces')
    op.execute('ALTER TABLE new_artpieces RENAME TO artpieces')


def downgrade():
    op.create_table('new_artpieces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column('submit_date', sa.DateTime(), nullable=False),
        sa.Column('art_encoding', sa.JSON(), nullable=False),
        sa.Column('submission_status'
        , sa.Enum('Submitted', 'Processing', 'Processed', name='submissionstatus')
        , nullable=False),
        sa.Column('raw_image', sa.LargeBinary(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute(("INSERT INTO "
        "new_artpieces("
        "id, title, submit_date, art_encoding, submission_status, raw_image, user_id) "
        "SELECT id, title, submit_date, art_encoding, submission_status, raw_image, user_id "
        "FROM artpieces ")
    )
    op.drop_table('artpieces')
    op.execute('ALTER TABLE new_artpieces RENAME TO artpieces')
