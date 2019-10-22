import schedule, time
from web import app
from flask import Flask
from flask_mail import Message, Mail
from web.utilities import sendConfirmationEmailToUser

# initiate mail with app config
mail = Mail()
app = Flask(__name__)
mail.init_app(app)

def sendEmailToASM(entry):
    msg = Message("ArtBot Agar Art Submission on Behalf of %s", entry.email)

    msg.recipients = [entry.email]
    msg.add_recipient("somebodyelse@asm.com")

    msg.html = "<h2>Attached is %s's argar art submission!</h2>", entry.email

    image = Image.frombytes("RGBX", (616, 414), entry.completed_picture)
    msg.attach("image.png", "image/png", image)

    mail.send(msg)

def sendEmailToUser(entry):
    msg = Message("ArtBot is done making your art!",
                recipients=[entry.email])

    msg.html = "<h2>Attached is a picture of your completed agart art and the original pixel art for comparison!</h2>"

    image = Image.frombytes("RGBX", (616, 414), entry.completed_picture)
    imageTwo = Image.frombytes("RGBX", (616, 414), entry.picture)
    msg.attach("completed_art.png", "image/png", image)
    msg.attach("original_pixel_art.png", "image/png", imageTwo)

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
    sendEmailToASM(entry)
    sendEmailToUser(entry)

schedule.every().day.at("7am").do(getArtSendEmail)
schedule.every().day.at("2pm").do(getArtSendEmail)
schedule.every().day.at("11pm").do(getArtSendEmail)

while True:
    schedule.run_pending()
    time.sleep(1)
