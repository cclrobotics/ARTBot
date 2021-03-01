from flask import current_app
import argon2

def get_state(app):
    """Gets the state for the application"""
    assert 'argon2' in app.extensions, \
        'The argon2 extension was not registered to the current ' \
        'application.  Please make sure to call init_app() first.'
    return app.extensions['argon2']

class _Argon2:
    def __init__(self, time_cost, memory_cost, parallelism, hash_len, salt_len, encoding):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.hash_len = hash_len
        self.salt_len = salt_len
        self.encoding = encoding
        self.exceptions = argon2.exceptions
        self.password_hasher = argon2.PasswordHasher(
                time_cost, memory_cost, parallelism, hash_len, salt_len, encoding
                )

class Argon2:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.state = self.init_app(app)
        else:
            self.state = None

    def init_argon2(self, config):
        return _Argon2(
            config.get('ARGON2_TIME_COST', argon2.DEFAULT_TIME_COST)
            , config.get('ARGON2_MEMORY_COST', argon2.DEFAULT_MEMORY_COST)
            , config.get('ARGON2_PARALLELISM', argon2.DEFAULT_PARALLELISM)
            , config.get('ARGON2_HASH_LENGTH', argon2.DEFAULT_HASH_LENGTH)
            , config.get('ARGON2_SALT_LENGTH', argon2.DEFAULT_RANDOM_SALT_LENGTH)
            , config.get('ARGON2_ENCODING', 'utf-8')
            )

    def init_app(self, app):
        state = self.init_argon2(app.config)

        #register extension with app
        app.extensions['argon2'] = state
        return state

    def get_app(self, reference_app=None):
        if reference_app is not None:
            return reference_app

        if current_app is not None:
            return current_app

        if self.app is not None:
            return self.app

        raise RuntimeError(
            'No application found. Either work inside a view function or push'
            ' an application context. See'
            ' http://flask-sqlalchemy.pocoo.org/contexts/.'
        )

    @property
    def exceptions(self, app=None):
        app = self.get_app(app)
        state = get_state(app)
        return state.exceptions
    
    @property
    def password_hasher(self, app=None):
        app = self.get_app(app)
        state = get_state(app)
        return state.password_hasher
