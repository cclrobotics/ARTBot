from flask import jsonify

def error_template(code, title):
    return {'errors': [{'code': code, 'title': title}]}

_MONTLY_SUBMISSION_LIMIT = error_template('monthly_limit', 'monthly submission limit exceeded')
_USER_LIMIT = error_template('user_limit', 'user limit exceeded')

_TOKEN_EXPIRATION = error_template('token_expired', 'confirmation token expiration')
_INVALID_TOKEN = error_template('token_invalid', 'invalid confirmation token')

_NOT_FOUND = error_template('not_found', 'resource not found')

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = self.message
        return jsonify(rv)

    @classmethod
    def reached_monthly_submission_limit(cls):
        return cls(_MONTLY_SUBMISSION_LIMIT, status_code=429)

    @classmethod
    def reached_user_limit(cls):
        return cls(_USER_LIMIT, status_code=429)

    @classmethod
    def confirmation_token_expired(cls):
        return cls(_TOKEN_EXPIRATION)

    @classmethod
    def resource_not_found(cls):
        return cls(_NOT_FOUND, status_code=404)

    @classmethod
    def invalid_confirmation_token(cls):
        return cls(_INVALID_TOKEN, status_code=404)

    @classmethod
    def from_validation_error(cls, err):
        message = dict({'errors': []})
        errors = message['errors']
        for code in err.messages.keys():
            for title in err.messages[code]:
                errors.append({'code': code, 'title': title})
        return cls(message)
