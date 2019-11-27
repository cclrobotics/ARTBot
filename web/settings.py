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
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """Mail settings."""
    MAIL_SERVER = os.environ.get('MAIL_SERVER', None)
    MAIL_PORT = os.environ.get('MAIL_PORT', 25)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', None)

    @classmethod
    def verbose_config(cls):
        print('#########################################')
        print('This is a %s environment' % (cls.ENV))
        print('The monthly submission limit is set to %d' % (cls.MONTLY_SUBMISSION_LIMIT))
        print('Expecting database @%s' % (cls.SQLALCHEMY_DATABASE_URI))
        cls.print_warnings()
        print('#########################################')

    @classmethod
    def is_secure_key(cls):
        return cls.SECRET_KEY != cls.UNSECURE_DEFAULT_SECRET_KEY

    @classmethod
    def print_warnings(cls):
        pass

    @classmethod
    def validate(cls):
        pass

class ProdConfig(Config):
    """Production configuration."""
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @classmethod
    def print_warnings(cls):
        if not cls.is_secure_key():
            print(("WARNING!\n"
                    "\tproduction servers should generate a random key\n"
                    "\texport WEB_SECRET =`python -c 'import os; print(os.urandom(16))'`"
                    )
            )

    @classmethod
    def validate(cls):
        assert cls.MAIL_SERVER != None, 'A mail server is required'
        assert cls.MAIL_USERNAME != None, 'A mail username is required'
        assert cls.MAIL_PASSWORD != None, 'A mail password is required'
        assert cls.MAIL_DEFAULT_SENDER != None, 'A mail default sender is required'

class DevConfig(Config):
    """Development configuration."""
    ENV = 'development'
    DB_NAME = 'ARTBot.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    """Mail settings."""
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = f'dev@{MAIL_SERVER}'

    @classmethod
    def print_warnings(cls):
        print(('Warning! Start local email server using:\n'
            '\t`python -m smtpd -n -c DebuggingServer localhost:1025`')
            )