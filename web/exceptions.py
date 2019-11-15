from flask import jsonify

def error_template(data, code=400):
    return {'message': {'errors': {'body': {'message': data}}}, 'status_code': code}

MONTLY_SUBMISSION_LIMIT_MESSAGE = (
    "Note: We're a small community lab run entirely by volunteers, and we can only make so many "
    "artpieces each month. This month we've hit our limit. You can still draw art here, but the "
    "website won't accept submissions. Come back next month and we'll start fresh!"
)
_USER_LIMIT_MESSAGE = (
    "Easy there, speed demon! We're a small volunteer-run, non-profit lab and there's a limit "
    "to how many works of art we can help make. Once we make your previous submission, submit "
    "another one! If there's an issue with your previous submission and you want to withdraw "
    "it, send us an email: ccl-artbot@gmail.com"
)

_MONTLY_SUBMISSION_LIMIT = error_template([MONTLY_SUBMISSION_LIMIT_MESSAGE], code=429)
_USER_LIMIT = error_template([_USER_LIMIT_MESSAGE], code=429)
_UNKNOWN_ERROR = error_template([], code=500)

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
        return cls(**_MONTLY_SUBMISSION_LIMIT)

    @classmethod
    def reached_user_limit(cls):
        return cls(**_USER_LIMIT)

    @classmethod
    def unknown_error(cls):
        return cls(**_UNKNOWN_ERROR)
