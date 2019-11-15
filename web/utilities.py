import datetime
from PIL import Image
from web.artpiece import (total_submission_count_since
        , active_submission_count
        , get_artpiece_by_id)

def first_of_month():
    return datetime.date.today().replace(day=1)

def has_reached_monthly_submission_limit(limit):
    return total_submission_count_since(first_of_month()) >= limit

def has_active_submission(email):
    return active_submission_count(email) != 0

#function to pull image off of database
def pull_picture(id):
    # handle invalid id
    artpiece = get_artpiece_by_id(id)
    image = Image.frombytes("RGBX", (616, 414), artpiece.raw_image)
    image.show()
    return image