import re

##taken from other utitlities function 
import os
import io
import json
import sqlalchemy as db
import pandas as pd
import math
from PIL import Image, ImageDraw
import sqlalchemy as db
from web import mail
from flask_mail import Message

basedir = os.path.abspath(os.path.dirname(__file__))

##
# String validations
#
##
def check_existence(data, name):
    strErr = 'Error: please enter a' + name

    if not data:
        return (strErr, 400)

    return False

def check_email(email):
    # the regex for emails we're using allows for lengths over 8000 characters
    # so we need to check for length first
    if len(email) > 254:
        return ('Error: invalid email address.', 400)

    if not re.match(r"^[a-zA-Z0-9._%+-]{1,64}@(?:[a-zA-Z0-9-]{1,63}\.){1,125}[a-zA-Z]{2,63}$", email):
        return ('Error: invalid email address.', 400)

    return False

def check_strings(string, name):
    lengthErr = 'Error: ' + name + ' is too long.  Must be less than 50 characters.'

    if len(string) > 50:
        return (lengthErr, 400)

    charErr = 'Error: ' + name + ' has invalid characters. Must be alphanumeric only.'

    if not re.match(r"^[a-zA-Z0-9]+$", string):
        return (charErr, 400)

    return False

def check_colors(colors):
    allowed_colors = [
      "pink",
      "orange",
      "teal",
      "yellow",
      "blue"
    ]

    for key in colors:
        if key not in allowed_colors: 
            return ('Error: bad request.', 400)
    return False

def check_coords(art):
    max_coords = (26, 39)

    for color in art:
        for coords in art[color]:
            if coords[0] > max_coords[0] or coords[1] > max_coords[1]:
                return ('Error: bad request.', 400)

    return False

def check_submission_limit(submission_cnt, submission_limit, email, prev_emails):
    limitErr = """We're a small volunteer-run, non-profit lab and there's a limit to how many works of art we can
                   help make. We're full-up this month, but come back on the 1st and we'll be open for art-making again!
                """

    if submission_cnt >= submission_limit:
        if(!check_coupon_code(title)):
            return (limitErr, 400)

    userLimitErr = """Easy there, speed demon! We're a small volunteer-run, non-profit lab and there's a limit to how
                    many works of art we can help make. Once we make your previous submission, submit another one! \n
                    If there's an issue with your previous submission and you want to withdraw it, send us an email:
                    ccl-artbot@gmail.com
                """

    if email in [email_obj[0] for email_obj in prev_emails]:
        if(!check_coupon_code(title)):
            return (userLimitErr, 400)

    return False

def check_coupon_code(title):
    availablecodes = models.site_vars.query.filter_by(var='code').val
    for code in availablecodes:
        if (title.endswith(code)):
            return True

    return False

def check_failed_validation(title, email, art, sub_cnt, sub_lim, prev_emails):
    
    check_one = check_existence(title, ' title')
    check_two = check_existence(email, 'n email')
    check_three = check_existence(art, 'n art design')
    
    check_four = check_strings(title, 'title')
    check_five = check_email(email)

    check_six = check_colors(art)
    check_seven = check_coords(art)

    check_eight = check_submission_limit(sub_cnt, sub_lim, email, prev_emails)
    check_nine = check_coupon_code(title)

    if check_one:
        return check_one
    elif check_two:
        return check_two
    elif check_three:
        return check_three
    elif check_four:
        return check_four
    elif check_five:
        return check_five
    elif check_six:
        return check_six
    elif check_seven:
        return check_seven
    elif check_eight:
        return check_eight
    elif check_nine:
        return check_nine
    else:
        return False

def rebuild_art(art):
    colors = {
        'pink': (255,192,203,1)
        ,'blue': (0,0,255,1)
        ,'teal': (0,128,128,1)
        ,'orange': (255,165,0,1)
        ,'yellow': (255,255,0,1)
    }

    scale = 40 * 5
    num_pixels = (39, 26)
    ratio = (3,2)
    pixel_size = (ratio[0] * scale / num_pixels[0]
                 ,ratio[1] * scale / num_pixels[1])
    total_size = (math.ceil(ratio[0] * scale + pixel_size[0])
                 ,math.ceil(ratio[1] * scale + pixel_size[1]))
    im = Image.new('RGBA',total_size,(255,255,255,1))
    draw = ImageDraw.Draw(im)

    for art_color in art:
        for pixel in art[art_color]:
            origin = [pixel_size[0] * pixel[1] , pixel_size[1] * pixel[0]] #pixels are given (y,x)
            far_corner = [pixel_size[0] + origin[0], pixel_size[1] + origin[1]]
            draw.rectangle(origin + far_corner,  fill = colors[art_color])
    return (im.tobytes())

#converts the image to bytes from database
def convert_bytes_to_image(im):
    art = Image.open(im, 'rb')
    im.show()

#function to pull image off of database
def pull_picture(id):
    #environment vars should be removed when implementing - they are already set at app config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.path.join(basedir, os.pardir, 'ARTBot.db'))
    SQL_ENGINE = db.create_engine(SQLALCHEMY_DATABASE_URI)

    query = f"""SELECT picture FROM artpieces
            WHERE id = {id}
            """
    picture = pd.read_sql(query, SQL_ENGINE).iloc[0][0]
    image = Image.frombytes("RGBX", (616, 414), picture)
    # image.show()
    return image

def sendConfirmationEmailToUser(entry):
    msg = Message(f"ArtBot Agar Art Submission on Behalf of {entry.email}")

    msg.recipients = [entry.email]

    msg.html = f"<h2>Confirmation ID: {entry.id}</h2><h2>Your art is attached. We'll send you another email when it's complete!</h2>"

    image = Image.frombytes("RGBX", (616, 414), entry.picture)
    with io.BytesIO() as output:
        image.save(output, format='JPEG')
        image_file = output.getvalue()
        msg.attach("image.jpg", "image/jpg", image_file)


    mail.send(msg)