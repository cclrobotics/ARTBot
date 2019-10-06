#Configures the database information for the website

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
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