from flask import (render_template, current_app)
from flask_mail import Message
from threading import Thread

from web.extensions import (mail, db)
from web.artpiece import (convert_raw_image_to_jpg, get_artpiece_by_id)
from web.user import User
from web.database.models import (EmailFailureModel, EmailFailureState)


def log_email_failure(fail_state, user_id=None, artpiece_id=None):
    def log_to_database(error_msg):
        EmailFailureModel(state=fail_state, error_msg=error_msg
                , artpiece_id=artpiece_id, user_id=user_id).save(commit=True)
    return log_to_database


def build_email(subject, sender, recipients, text_body, html_body, attachments=None):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    return msg


def safe_send_email(email, error_handler):
    try:
        mail.send(email)
    except Exception as e:
        error_handler(repr(e))


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

    def log_confirmation_email_failure(artpiece):
        return log_email_failure(
                EmailFailureState.submission_confirmation, artpiece.user_id, artpiece.id)

    artpiece = get_artpiece_by_id(artpiece_id)
    user = User.get_by_id(artpiece.user_id)
    safe_send_email(
            build_confirmation_email(user, artpiece)
            , log_confirmation_email_failure(artpiece)
            )


def with_context(app, cleanup=lambda : None):
    def wrapper(func, *args):
        with app.app_context():
            func(*args) if args else func()
            cleanup()
    return wrapper


def send_confirmation_email_async(artpiece):
    Thread(target=with_context(current_app._get_current_object(), db.session.remove)
            , args=(send_confirmation_email, artpiece.id)).start()
