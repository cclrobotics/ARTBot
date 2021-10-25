import re
from .exceptions import (PixelOutOfBoundsException, ColorSchemeException, BlankCanvasException,
        InvalidTitleException, InvalidCanvasException)

MAX_CANVAS_SIZE = 100

def validate_art_content_length(art):
    def has_content(art):
        for _, pixels in art.items():
            if len(pixels) > 0:
                return True
        return False

    if not art or not has_content(art):
        raise BlankCanvasException()


def validate_color_keys(art, valid_color_keys):
    def has_matching_color_scheme(art, valid_color_keys):
        for color_key in art:
            if color_key not in valid_color_keys:
                return False
        return True

    if not has_matching_color_scheme(art, valid_color_keys):
        raise ColorSchemeException()

def validate_pixels(art, canvas_size):
    def has_pixels_within_canvas(pixels, canvas_size):
        # pixels are given as [y,x]
        for y, x in pixels:
            if x > canvas_size['x'] or y > canvas_size['y']: #check for negative values?
                return False
        return True

    for color in art:
        if not has_pixels_within_canvas(art[color], canvas_size):
            raise PixelOutOfBoundsException()

_ALPHA_NUM_REGEX = re.compile(r"^[\w\s]+$")

def validate_title(title):
    if not title or not (0 < len(title) < 50):
        raise InvalidTitleException('title_length', 'Title not within length criteria')
    if not _ALPHA_NUM_REGEX.match(title):
        raise InvalidTitleException('title_chars'
            , 'Title is limited to alpha-numeric characters only')

def validate_canvas_size(size):
    if 'x' not in size or 'y' not in size:
        raise InvalidCanvasException()
    if size['x'] > MAX_CANVAS_SIZE or size['y'] > MAX_CANVAS_SIZE:
        raise InvalidCanvasException()