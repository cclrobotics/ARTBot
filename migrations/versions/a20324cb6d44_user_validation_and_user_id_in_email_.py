"""user validation and user id in email removal

Revision ID: a20324cb6d44
Revises: 4a7a8b53b4f8
Create Date: 2019-11-24 16:30:45.892933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a20324cb6d44'
down_revision = '4a7a8b53b4f8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('new_emailfailures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artpiece_id', sa.Integer(), nullable=False),
    sa.Column('failure_state', sa.Enum('s_confirmation', 'bioart_completion', name='emailfailurestate'), nullable=False),
    sa.Column('error_msg', sa.String(length=150), nullable=False),
    sa.ForeignKeyConstraint(['artpiece_id'], ['artpieces.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute(("INSERT INTO "
        "new_emailfailures("
        "id, artpiece_id, failure_state, error_msg) "
        "SELECT id, artpiece_id, failure_state, error_msg "
        "FROM emailfailures")
    )
    op.drop_table('emailfailures')
    op.execute('ALTER TABLE new_emailfailures RENAME TO emailfailures')

    op.create_table('new_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute(("INSERT INTO "
        "new_users(id, email, created_at) "
        "SELECT id, email, created_at "
        "FROM users"))
    op.drop_table('users')
    op.execute('ALTER TABLE new_users RENAME TO users')

    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.create_table('new_emailfailures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('artpiece_id', sa.Integer(), nullable=True),
    sa.Column('failure_state', sa.Enum('s_confirmation', 'bioart_completion', name='emailfailurestate'), nullable=False),
    sa.Column('error_msg', sa.String(length=150), nullable=False),
    sa.ForeignKeyConstraint(['artpiece_id'], ['artpieces.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute(("INSERT INTO "
        "new_emailfailures("
        "id, artpiece_id, failure_state, error_msg) "
        "SELECT id, artpiece_id, failure_state, error_msg "
        "FROM emailfailures")
    )
    op.drop_table('emailfailures')
    op.execute('ALTER TABLE new_emailfailures RENAME TO emailfailures')

    op.create_table('new_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute(("INSERT INTO "
        "users(id, email, created_at, verified) "
        "SELECT id, email, created_at, True as verified "
        "FROM users"))
    op.drop_table('users')
    op.execute('ALTER TABLE new_users RENAME TO users')
