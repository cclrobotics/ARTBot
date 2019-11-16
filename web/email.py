from flask import render_template, current_app
from flask_mail import Message
from web.extensions import mail
from threading import Thread

from web.artpiece import convert_raw_image_to_jpg

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
        attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email
                , args=(current_app._get_current_object(), msg)).start()


def send_confirmation_email(user, submission):
    image_file = convert_raw_image_to_jpg(submission.raw_image)
    send_email(f'ARTBot Submission Confirmation for "{submission.title}"'
            , sender=current_app.config['MAIL_DEFAULT_SENDER']
            , recipients=[user.email]
            , text_body=render_template(
                'email/submission_confirmation.txt', submission=submission)
            , html_body=render_template(
                'email/submission_confirmation.html', submission=submission)
            , attachments=[('pixel-art.jpg', 'image/jpg', image_file)])
