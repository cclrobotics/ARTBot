import datetime
import io
import math
from PIL import Image, ImageDraw
from web.extensions import mail
from flask_mail import Message
from flask import current_app
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

def sendConfirmationEmailToUser(entry):
    msg = Message(f"ARTBot Submission Confirmation for {entry.title}"
            , sender=current_app.config['MAIL_DEFAULT_SENDER']
            , recipients=[entry.email])

    msg.html = f"""
                <h2>The Counter Culture Lab BioArtBot team thanks you for your submission!</h2>
                <h2>Confirmation ID: {entry.id}</h2>
                <h2>The pixel version of your artwork is attached.
                    We'll send you another email with pictures when the bio version is complete!</h2>
                <h4>Questions or concerns?  Email us at
                    <a href="mailto:ccl-artbot@gmail.com"
                        ccl-artbot@gmail.com
					</a>
                </h4>
                """

    image = Image.frombytes("RGBX", (616, 414), entry.raw_image)
    with io.BytesIO() as output:
        image.save(output, format='JPEG')
        image_file = output.getvalue()

    msg.attach("image.jpg", "image/jpg", image_file)
    mail.send(msg)