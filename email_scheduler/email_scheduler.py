import schedule, time
from web import app
from flask import Flask
from flask_mail import Message, Mail
from PIL import Image, ImageDraw
import os
import sqlalchemy as db
import pandas as pd
from web.utilities import sendConfirmationEmailToUser

# initiate mail with app config
mail = Mail()
app = Flask(__name__)
mail.init_app(app)

def sendEmailToUser(entry):
    msg = Message("ARTBot is done making your art!",
                recipients=[entry.email])

    msg.html = f"""
                <h2>The Counter Culture Lab ARTBot team thanks you for your submission!</h2>
                <h2>Attached is a picture of your completed agart art and the original pixel art for comparison!</h2>
                <h4>Questions or concerns?  Email us at 
                    <a href="mailto:ccl-artbot@gmail.com"
                        ccl-artbot@gmail.com
					</a>
                </h4>
                """

    image = Image.frombytes("RGBX", (616, 414), entry.completed_picture)
    with io.BytesIO() as output:
        image.save(output, format='JPEG')
        image_file = output.getvalue()
        msg.attach("completed_art.jpg", "image/jpg", image_file)
    
    imageTwo = Image.frombytes("RGBX", (616, 414), entry.picture)
    with io.BytesIO() as outputTwo:
        imageTwo.save(output, format='JPEG')
        image_fileTwo = outputTwo.getvalue()
        msg.attach("original_pixel_art.jpg", "image/jpg", image_fileTwo)

    mail.send(msg)

def getCompletedArt():
    #environment vars should be removed when implementing - they are already set at app config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.path.join(basedir, os.pardir, 'ARTBot.db'))
    SQL_ENGINE = db.create_engine(SQLALCHEMY_DATABASE_URI)

    query = f"""SELECT picture FROM artpieces
            WHERE picture IS NOT NULL AND status <> 'Completed'
            """
    entry = pd.read_sql(query, SQL_ENGINE).iloc[0]
    return entry

def getArtSendEmail():
    entry = getCompletedArt()
    sendEmailToUser(entry)

schedule.every().day.at("7am").do(getArtSendEmail)
schedule.every().day.at("2pm").do(getArtSendEmail)
schedule.every().day.at("11pm").do(getArtSendEmail)

while True:
    schedule.run_pending()
    time.sleep(1)
