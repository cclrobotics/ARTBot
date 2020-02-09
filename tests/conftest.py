import pytest
from flask_migrate import upgrade
from web.app import create_app
from web.extensions import db

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.from_object('web.settings.TestingConfig')
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def test_database():
    upgrade()
    yield db
    db.session.remove()
    db.reflect()
    db.drop_all()

@pytest.fixture(scope='function')
def clear_database():
    yield
    db.session.rollback()
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
