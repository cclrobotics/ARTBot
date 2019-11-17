from flask import (render_template, current_app)
from flask_mail import Message
from threading import Thread

from web.extensions import mail
from web.artpiece import (convert_raw_image_to_jpg, get_artpiece_by_id)
from web.user import User


def build_email(subject, sender, recipients, text_body, html_body, attachments=None):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    return msg


def send_confirmation_email(artpiece_id):
    def build_confirmation_email(user, submission):
        image_file = convert_raw_image_to_jpg(submission.raw_image)
        email = build_email(f'ARTBot Submission Confirmation for "{submission.title}"'
                , sender=current_app.config['MAIL_DEFAULT_SENDER']
                , recipients=[user.email]
                , text_body=render_template(
                    'email/submission_confirmation.txt', submission=submission)
                , html_body=render_template(
                    'email/submission_confirmation.html', submission=submission)
                , attachments=[('pixel-art.jpg', 'image/jpg', image_file)])
        return email

    artpiece = get_artpiece_by_id(artpiece_id)
    user = User.get_by_id(artpiece.user_id)
    mail.send(build_confirmation_email(user, artpiece))


def with_context(app, cleanup=lambda : None):
    def wrapper(func, *args):
        with app.app_context():
            func(*args) if args else func()
            cleanup()
    return wrapper


def send_confirmation_email_async(artpiece):
    Thread(target=with_context(current_app._get_current_object())
            , args=(send_confirmation_email, artpiece.id)).start()
