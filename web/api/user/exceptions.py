from flask import jsonify

def error_template(code, title):
    return {'errors': [{'code': code, 'title': title}]}

_NOT_FOUND = error_template('not_found', 'resource not found')

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
    def from_validation_error(cls, err):
        message = dict({'errors': []})
        errors = message['errors']
        for code in err.messages.keys():
            for title in err.messages[code]:
                errors.append({'code': code, 'title': title})
        return cls(message)
