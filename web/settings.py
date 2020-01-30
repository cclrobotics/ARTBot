"""Application configuration."""

import os

class Config(object):
    """Base configuration."""
    ENV = 'default'
    UNSECURE_DEFAULT_SECRET_KEY = 'invalid-secret-key'
    SECRET_KEY = os.environ.get('WEB_SECRET', UNSECURE_DEFAULT_SECRET_KEY)
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    MONTLY_SUBMISSION_LIMIT = int(os.environ.get('WEB_MONTHLY_SUBMISSION_LIMIT', 27))
    # this should be moved to the database
    COLOR_SCHEME = {
        'pink': (255,192,203,1)
        ,'blue': (0,0,255,1)
        ,'teal': (0,128,128,1)
        ,'orange': (255,165,0,1)
        ,'yellow': (255,255,0,1)
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """Mail settings."""
    MAIL_SERVER = os.environ.get('MAIL_SERVER', None)
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
    MAIL_USE_TLS = bool(os.environ.get('MAIL_USE_TLS', False))
    MAIL_USE_SSL = bool(os.environ.get('MAIL_USE_SSL', False))
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', None)

class ProdConfig(Config):
    """Production configuration."""
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class DevConfig(Config):
    """Development configuration."""
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')