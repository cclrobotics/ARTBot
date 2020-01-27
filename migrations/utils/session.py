from contextlib import contextmanager
from alembic import op
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=op.get_bind())

@contextmanager
def session_scope():
    """Provide transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
