import datetime
from PIL import Image
from .artpiece import Artpiece

def first_of_month():
    return datetime.date.today().replace(day=1)

def get_monthly_submission_count():
    return Artpiece.total_submission_count_since(first_of_month())

def has_reached_monthly_submission_limit(limit):
    return get_monthly_submission_count() >= limit

#function to pull image off of database
def pull_picture(id):
    # handle invalid id
    artpiece = Artpiece.get_by_id(id)
    image = Image.frombytes("RGBX", (616, 414), artpiece.raw_image)
    image.show()
    return image