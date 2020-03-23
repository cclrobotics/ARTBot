from ..exceptions import (InvalidUsage, error_template)

_MONTLY_SUBMISSION_LIMIT = error_template('monthly_limit', 'monthly submission limit exceeded')
_USER_LIMIT = error_template('user_limit', 'user limit exceeded')

_PIXEL_OUT_OF_BOUNDS = error_template('pixel_out_of_bounds', 'pixel out of canvas bounds')
_INVALID_COLOR_SCHEME = error_template('invalid_color_scheme', 'invalid color scheme')
_BLANK_CANVAS = error_template('blank_canvas', 'blank canvas')

_TOKEN_EXPIRATION = error_template('token_expired', 'confirmation token expiration')
_INVALID_TOKEN = error_template('token_invalid', 'invalid confirmation token')

class MonthlySubmissionLimitException(InvalidUsage):
    def __init__(self):
        super().__init__(_MONTLY_SUBMISSION_LIMIT, status_code=429)

class UserSubmissionLimitException(InvalidUsage):
    def __init__(self):
        super().__init__(_USER_LIMIT, status_code=429)

class PixelOutOfBoundsException(InvalidUsage):
    def __init__(self):
        super().__init__(_PIXEL_OUT_OF_BOUNDS)

class ColorSchemeException(InvalidUsage):
    def __init__(self):
        super().__init__(_INVALID_COLOR_SCHEME)

class BlankCanvasException(InvalidUsage):
    def __init__(self):
        super().__init__(_BLANK_CANVAS)

class InvalidTitleException(InvalidUsage):
    def __init__(self, code, title):
        super().__init__(error_template(code, title))

class ExpiredConfirmationTokenException(InvalidUsage):
    def __init__(self):
        super().__init__(_TOKEN_EXPIRATION)

class InvalidConfirmationTokenException(InvalidUsage):
    def __init__(self):
        super().__init__(_INVALID_TOKEN)
