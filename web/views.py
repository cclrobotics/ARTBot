#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

from flask import (render_template, Blueprint, current_app, request)
from .api.user.artpiece import DEFAULT_CANVAS

from web.database.models import SubmissionStatus

main = Blueprint('main', __name__)

#Home page
@main.route('/', methods=('GET', ))
@main.route('/index', methods=('GET', ))
def index():
    return render_template('main.html', canvas_size=DEFAULT_CANVAS)

@main.route('/receive_art', methods=('POST', ))
def receive_art():

@main.route('/art_confirmation', methods=('GET', ))
def art_confirmation():
    args = request.args
    token = args.get('token')
    artpiece_id = args.get('id')

    user = User.get_by_email(data['email']) or User.from_email(data['email'])

    payable_error = None
    if has_reached_monthly_submission_limit(current_app.config['MONTLY_SUBMISSION_LIMIT']):
        payable_error = InvalidUsage.reached_monthly_submission_limit()
    if user.has_active_submission():
        payable_error = InvalidUsage.reached_user_limit()
    status = SubmissionStatus.awaiting_payment if payable_error else SubmissionStatus.submitted #TODO: DB doesn't seem happy with new submission status I added.

    artpiece = user.create_artpiece(data['title'], data['art'], status)

    if payable_error:
        if 'paypal' not in payable_error.message['errors']['body']['message'][0]: #hotfix for unlimited appending of buttons
            payable_error.message['errors']['body']['message'][0] += render_template('paypal_form.html', id=artpiece._model_id)
            artpiece.status = SubmissionStatus.awaiting_payment
            db.session.commit()
        raise payable_error
        #TODO: How do submissions that don't get paid for get removed if done this way. If check is before db commit, how do we get a unique ID?

    db.session.commit()

    send_confirmation_email_async(artpiece)

    return jsonify({'success': 'We will send you a confirmation email'}), 201

@main.route('/confirm_art/<token>', methods=('GET', ))
def confirm_art(token):
    try:
        artpiece = Artpiece.verify_confirmation_token(token)
    except ExpiredSignatureError:
        return render_template('confirmation_expired.html')
    except PyJWTError:
        return render_template('404.html')

    artpiece.confirm()
    db.session.commit()
    return render_template('artpiece_confirmed.html')

#TODO: make view to receive payment confirmation from PayPal and use that to mark that status from hold and send confirm email
@main.route('/payment_confirm', methods=('POST',))
def payment_confirm():
    '''This module processes PayPal Instant Payment Notification messages (IPNs).'''

    import requests

    VERIFY_URL_PROD = 'https://ipnpb.paypal.com/cgi-bin/webscr'
    VERIFY_URL_TEST = 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr'

    # Switch as appropriate
    VERIFY_URL = VERIFY_URL_TEST

    # CGI preamble
    print('content-type: text/plain')
    print()

    # Read and copy query string
    params = dict(request.form)
    params['cmd'] = '_notify-validate' # Add '_notify-validate' parameter

    # Post back to PayPal for validation
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'user-agent': 'Python-IPN-Verification-Script'}
    r = requests.post(VERIFY_URL, params=params, headers=headers, verify=True)
    r.raise_for_status()

    # Check return message and take action as needed, then return 200 to Paypal's original request to close out
    if r.text == 'VERIFIED':
        print('Verified payment') #need to check the payer id, which should be part of the orignal button
        #If payment successful, mark approved and send email. If unsuccessful, but valid transaction, send a "your payment didn't work" email.
        artpiece = Artpiece.get_by_id(params.invoice)
        artpiece.status = SubmissionStatus.submitted
        send_confirmation_email_async(artpiece)
        return 'Verified'
    elif r.text == 'INVALID':
        print('Invalid payment') #If payer id is a real payer id, but there's an issue, send an email to user?
        return 'Invalid'
    else:
        return 'Unexpected Response', 400

#TODO: when they submit over the monthly limit, the link that they click routes through a special "I will pay" submission
#       that calls /receive_art again with a bypass on limit and a status of "HOLD", then routes user to Paypal

#TODO: Figure out PayPal side of the flow before deciding how user gets routed back with confirmation. Should show
#      something a lot like the regular success screen

@main.route('/paypal_demo', methods=('GET',))
def paypay_demo():

    return """<form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick" />
<input type="hidden" name="hosted_button_id" value="L3YHLPDSVSAKW" />
<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
<img alt="" border="0" src="https://www.sandbox.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1" />
</form>
"""
