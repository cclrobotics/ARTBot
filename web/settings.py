"""Application configuration."""

import os

ANNOUNCEMENT = os.environ.get('ANNOUNCEMENT', None)

class Config(object):
    """Base configuration."""
    ENV = 'default'
    UNSECURE_DEFAULT_SECRET_KEY = 'invalid-secret-key'
    SECRET_KEY = os.environ.get('WEB_SECRET', UNSECURE_DEFAULT_SECRET_KEY)
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    MONTLY_SUBMISSION_LIMIT = int(os.environ.get('WEB_MONTHLY_SUBMISSION_LIMIT', 27))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """JWT settings."""
    UNSECURE_DEFAULT_JWT_SECRET_KEY = 'invalid-jwt-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET', UNSECURE_DEFAULT_JWT_SECRET_KEY)

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

class TestingConfig(Config):
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')