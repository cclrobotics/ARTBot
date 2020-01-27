from contextlib import contextmanager
from alembic import op
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=op.get_bind())

@contextmanager
def session_scope():
    """Provide transactional scope around a series of operations."""
    session = Session()
    yield session
    session.flush()
