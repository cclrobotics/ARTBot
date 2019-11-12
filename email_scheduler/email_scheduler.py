import schedule, time, io
from flask import Flask
from flask_mail import Message, Mail
from PIL import Image, ImageDraw
import os
import sqlalchemy as sa
import pandas as pd
from web.utilities import sendConfirmationEmailToUser

# initiate mail with app config
mail = Mail()
app = Flask(__name__)
app.config.from_object('web.config')
mail.init_app(app)

SQL_ENGINE = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

def sendEmailToUser(entry):
    with app.app_context():
        msg = Message("BioArtBot is done making your art!",
                    recipients=[entry.email])

        msg.html = """
                    <h2>The Counter Culture Labs BioArtBot team thanks you for your submission!</h2>
                    <h2>Attached is a picture of your completed agart art and the original pixel art for comparison!</h2>
                    <h4>Questions or concerns?  Email us at 
                        <a href="mailto:ccl-artbot@gmail.com"
                            ccl-artbot@gmail.com
                        </a>
                    </h4>
                    """

        image = Image.frombytes("RGBX", (616, 414), entry.photo)
        with io.BytesIO() as output:
            image.save(output, format='JPEG')
            image_file = output.getvalue()
            msg.attach("completed_art.jpg", "image/jpg", image_file)

        imageTwo = Image.frombytes("RGBX", (616, 414), entry.picture)
        with io.BytesIO() as outputTwo:
            imageTwo.save(outputTwo, format='JPEG')
            image_fileTwo = outputTwo.getvalue()
            msg.attach("original_pixel_art.jpg", "image/jpg", image_fileTwo)

        mail.send(msg)

        SQL_ENGINE.execute(
            f"UPDATE artpieces SET status = 'Complete' where id = {entry.id}"
        )


def getCompletedArt():
    query = """SELECT * FROM artpieces
            WHERE photo IS NOT NULL AND status = 'Incubated'
            """
    entries = pd.read_sql(query, SQL_ENGINE)
    return entries

def getArtSendEmail():
    print('Sending email batch')
    entries = getCompletedArt()
    if len(entries):
        entries.apply(sendEmailToUser, axis=1)

schedule.every().day.at("07:00").do(getArtSendEmail)
schedule.every().day.at("14:00").do(getArtSendEmail)
schedule.every().day.at("23:00").do(getArtSendEmail)

while True:
    schedule.run_pending()
    time.sleep(1)
