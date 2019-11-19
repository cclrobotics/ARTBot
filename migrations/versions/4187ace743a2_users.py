"""Users

Revision ID: 4187ace743a2
Revises: fca4d39d6f19
Create Date: 2019-11-15 11:32:49.103079

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4187ace743a2'
down_revision = 'fca4d39d6f19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###
    op.execute(("INSERT INTO "
        "users(email, created_at, verified) "
        "SELECT email, MIN(submit_date), True as verified "
        "FROM artpieces "
        "GROUP BY email"))
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
        "title, submit_date, art_encoding, submission_status, raw_image, user_id) "
        "SELECT artpieces.title, artpieces.submit_date, artpieces.art_encoding, artpieces.submission_status, artpieces.raw_image, users.id "
        "FROM artpieces "
        "INNER JOIN users "
        "ON artpieces.email=users.email")
    )
    op.drop_table('artpieces')
    op.execute('ALTER TABLE new_artpieces RENAME TO artpieces')


def downgrade():
    op.create_table('new_artpieces',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(50), nullable=False),
            sa.Column('email', sa.String(50), nullable=False),
            sa.Column('submit_date', sa.DateTime(), nullable=False),
            sa.Column('art_encoding', sa.JSON(), nullable=False),
            sa.Column('submission_status'
            , sa.Enum('Submitted', 'Processing', 'Processed', name='submissionstatus')
            , nullable=False),
            sa.Column('raw_image', sa.LargeBinary(), nullable=False),
            sa.PrimaryKeyConstraint('id')
            )
    op.execute(("INSERT INTO "
        "new_artpieces("
        "title, email, submit_date, art_encoding, submission_status, raw_image) "
        "SELECT artpieces.title, users.email, artpieces.submit_date, artpieces.art_encoding, artpieces.submission_status, artpieces.raw_image "
        "FROM artpieces "
        "INNER JOIN users "
        "ON artpieces.user_id=users.id")
    )
    op.drop_table('artpieces')
    op.execute('ALTER TABLE new_artpieces RENAME TO artpieces')
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###