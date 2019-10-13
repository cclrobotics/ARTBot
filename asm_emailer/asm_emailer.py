import schedule, time
from web import app
from Flask import Flask
from flask_mail import Message, Mail

# initiate mail with app config
mail = Mail()
app = Flask(__name__)
mail.init_app(app)

def sendEmail():
    msg = Message("Hello",
                sender="from@example.com",
                recipients=["to@example.com"])

    msg.recipients = ["you@example.com"]
    msg.add_recipient("somebodyelse@example.com")

    msg.html = "<b>testing</b>"

    mail.send(msg)

def getCompletedArt():

def getArtSendEmail():

schedule.every().day.at("7am").do(getArtSendEmail)
schedule.every().day.at("2pm").do(getArtSendEmail)
schedule.every().day.at("11pm").do(getArtSendEmail)

while True:
    schedule.run_pending()
    time.sleep(1)
