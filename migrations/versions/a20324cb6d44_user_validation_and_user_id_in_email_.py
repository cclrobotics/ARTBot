"""user validation and user id in email removal

Revision ID: a20324cb6d44
Revises: 4a7a8b53b4f8
Create Date: 2019-11-24 16:30:45.892933

"""
# revision identifiers, used by Alembic.
revision = 'a20324cb6d44'
down_revision = '4a7a8b53b4f8'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from migrations.utils.session import session_scope

Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    verified = sa.Column(sa.Boolean(), nullable=False)


def upgrade():
    op.drop_column('emailfailures', 'user_id')
    op.drop_column('users', 'verified')

def downgrade():
    op.add_column('users', sa.Column('verified', sa.Boolean, nullable=True))

    with session_scope() as session:
        users = session.query(UserModel).all()
        for user in users:
            user.verified = True

    op.alter_column('users', 'verified', nullable=False)
    op.add_column('emailfailures', sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'),
        nullable=True))
