#Configures the database information for the website

import os
basedir = os.path.abspath(os.path.dirname(__file__))

try:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
except:
    print('No database connection provided. Using local SQLite database')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.path.join(basedir, os.pardir, 'ARTBot.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True
SECRET_KEY = 'my_secret'

#This accounts for if the static images and audio need to be saved somewhere besides the directory where the code is stored.
#It checks the parent directory of the code directory for a folder that matches alternate_path. If it exists, it uses
#it. Otherwise it uses the basedir
alternate_path = "public_html"
if os.path.exists(os.path.join(os.path.split(basedir)[0],alternate_path)):
    static_basedir = os.path.join(os.path.split(basedir)[0],alternate_path)
else:
    static_basedir = basedir

IMAGE_UPLOAD_FOLDER = os.path.join(static_basedir,'static','img')
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'svg'])

SUBMISSION_LIMIT = 27
LIMIT_MESSAGE = """Note: We're a small community lab run entirely by volunteers, and we can only make so many artpieces
                    each month. This month we've hit our limit. You can still draw art here, but the website won't
                    accept submissions. Come back next month and we'll start fresh!"""


try:
    MAIL_SERVER = os.environ['EMAIL_SERVER']
    MAIL_PORT = os.environ['EMAIL_PORT']
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    # MAIL_DEBUG : default app.debug
    MAIL_USERNAME = os.environ['EMAIL_USER']
    MAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = os.environ['EMAIL_SENDER']
    # MAIL_MAX_EMAILS : default None
    # MAIL_SUPPRESS_SEND : default app.testing
    # MAIL_ASCII_ATTACHMENTS : default False
except:
    print("Missing or incomplete email config. Emails won't send")