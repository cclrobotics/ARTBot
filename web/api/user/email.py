from flask import (render_template, current_app, url_for)
from flask_mail import Message
from threading import Thread

from web.extensions import (mail, db)
from .artpiece import Artpiece
from .user import User
from web.database.models import (EmailFailureModel, EmailFailureState)


def log_email_failure(fail_state, artpiece_id=None):
    def log_to_database(error_msg):
        EmailFailureModel(state=fail_state, error_msg=error_msg
                , artpiece_id=artpiece_id).save(commit=True)
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


def send_confirmation_email(artpiece, confirmation_url):
    def build_confirmation_email(artpiece, confirmation_url):
        image_file = artpiece.get_image_as_jpg()
        email = build_email(f'Submission: "{artpiece.title}"'
                , sender=('ArtBot Confirmation', current_app.config['MAIL_DEFAULT_SENDER'])
                , recipients=[artpiece.creator.email]
                , text_body=render_template(
                    'email/submission_confirmation.txt', confirmation_url=confirmation_url)
                , html_body=render_template(
                    'email/submission_confirmation.html'
                    , submission=artpiece
                    , confirmation_url=confirmation_url
                    )
                , attachments=[('pixel-art.jpg', 'image/jpg', image_file)])
        return email

    def log_confirmation_email_failure(artpiece):
        return log_email_failure(
                EmailFailureState.submission_confirmation, artpiece._model.id)

    safe_send_email(
            build_confirmation_email(artpiece, confirmation_url)
            , log_confirmation_email_failure(artpiece)
            )


def with_context(app, prepare=lambda : None, cleanup=lambda : None):
    def wrapper(func, *args):
        with app.app_context():
            prepare()
            func(*args) if args else func()
            cleanup()
    return wrapper


def send_confirmation_email_async(artpiece):
    confirmation_url = url_for(
            'main.art_confirmation'
            , token=artpiece.get_confirmation_token()
            , id=artpiece.id
            , _external=True)
    Thread(target=with_context(
        current_app._get_current_object(), artpiece.refresh, db.session.remove)
        , args=(send_confirmation_email, artpiece, confirmation_url)).start()
