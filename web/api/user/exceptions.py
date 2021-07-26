from flask import jsonify

def error_template(code, title):
    return {'errors': [{'code': code, 'title': title}]}

_NOT_FOUND = error_template('not_found', 'resource not found')
_BAD_LOGIN = error_template('bad_credentials', 'bad username or password')
_BAD_TOKEN = error_template('bad_token', 'no match for provided data token')
_USER_NOT_FOUND = error_template('user_not_found', 'requested user not found')
_USER_EXISTS = error_template('user_exists', 'cannot create user that already exists')
_FORBIDDEN = error_template('forbidden', 'user does not have access')

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = self.message
        return jsonify(rv)

    @classmethod
    def resource_not_found(cls):
        return cls(_NOT_FOUND, status_code=404)

    @classmethod
    def bad_token(cls):
        return cls(_BAD_TOKEN, status_code=403)
    
    @classmethod
    def bad_login(cls):
        return cls(_BAD_LOGIN, status_code=403)

    @classmethod
    def forbidden(cls):
        return cls(_FORBIDDEN, status_code=403)

    @classmethod
    def user_not_found(cls):
        return cls(_USER_NOT_FOUND, status_code=422)
    
    @classmethod
    def user_exists(cls):
        return cls(_USER_EXISTS, status_code=422)
    
    @classmethod
    def from_validation_error(cls, err):
        message = dict({'errors': []})
        errors = message['errors']
        for code in err.messages.keys():
            for title in err.messages[code]:
                errors.append({'code': code, 'title': title})
        return cls(message)