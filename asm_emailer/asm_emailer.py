import schedule, time
from web import app
from Flask import Flask
from flask_mail import Message, Mail

mail = Mail()
app = Flask(__name__)
mail.init_app(app)

msg = Message("Hello",
            sender="from@example.com",
            recipients=["to@example.com"])

msg.recipients = ["you@example.com"]
msg.add_recipient("somebodyelse@example.com")

msg.html = "<b>testing</b>"

mail.send(msg)
