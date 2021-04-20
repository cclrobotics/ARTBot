import pytest
import os
from flask import current_app
from flask_migrate import upgrade
from web.app import create_app
from web.extensions import db

@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    app.config.from_object('web.settings.TestingConfig')
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
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

@pytest.fixture(scope='session')
def test_directory():
    APP_DIR = current_app.config['APP_DIR']
    path = os.path.join(APP_DIR,'robot/procedures')
    existing_files = os.listdir(path)
    yield path
    for f in os.listdir(path):
        if f not in existing_files:
            os.remove(os.path.join(path, f))
