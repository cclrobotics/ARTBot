import re


##
# String validations
#
##
def check_existence(data, name):
    strErr = 'Error: please enter a' + name

    if not data:
        return (strErr, 400)

    return False

def check_email(email):
    # the regex for emails we're using allows for lengths over 8000 characters
    # so we need to check for length first
    if len(email) > 254:
        return ('Error: invalid email address.', 400)

    if not re.match(r"^[a-zA-Z0-9._%+-]{1,64}@(?:[a-zA-Z0-9-]{1,63}\.){1,125}[a-zA-Z]{2,63}$", email):
        return ('Error: invalid email address.', 400)

    return False

def check_strings(string, name):
    lengthErr = 'Error: ' + name + ' is too long.  Must be less than 50 characters.'

    if len(string) > 50:
        return (lengthErr, 400)

    charErr = 'Error: ' + name + ' has invalid characters. Must be alphanumeric only.'

    if not re.match(r"^[a-zA-Z0-9]+$", string):
        return (charErr, 400)

    return False

def check_colors(colors):
    allowed_colors = [
      "pink",
      "orange",
      "teal",
      "yellow",
      "blue"
    ]

    for key in colors:
        if key not in allowed_colors: 
            return ('Error: bad request.', 400)
    return False

def check_coords(art):
    max_coords = (39, 26)

    for color in art:
        for coords in art[color]:
            if coords[0] > max_coords[0] or coords[1] > max_coords[1]:
                return ('Error: bad request.', 400)

    return False

def check_submission_limit(submission_cnt, submission_limit, email, prev_emails):
    limitErr = """We're a small volunteer-run, non-profit lab and there's a limit to how many works of art we can
                   help make. We're full-up this month, but come back on the 1st and we'll be open for art-making again!
                """

    if submission_cnt >= submission_limit:
        return (limitErr, 400)

    userLimitErr = """Easy there, speed demon! We're a small volunteer-run, non-profit lab and there's a limit to how
                    many works of art we can help make. Once we make your previous submission, submit another one! \n
                    If there's an issue with your previou submission and you want to withdraw it, send us an email:
                    ccl-artbot@gmail.com
                """

    if email in [email_obj[0] for email_obj in prev_emails]:
        return (userLimitErr, 400)

    return False

def check_failed_validation(title, email, art, sub_cnt, sub_lim, prev_emails):
    
    check_one = check_existence(title, ' title')
    check_two = check_existence(email, 'n email')
    check_three = check_existence(art, 'n art design')
    
    check_four = check_strings(title, 'title')
    check_five = check_email(email)

    check_six = check_colors(art)
    check_seven = check_coords(art)

    check_eight = check_submission_limit(sub_cnt, sub_lim, email, prev_emails)

    if check_one:
        return check_one
    elif check_two:
        return check_two
    elif check_three:
        return check_three
    elif check_four:
        return check_four
    elif check_five:
        return check_five
    elif check_six:
        return check_six
    elif check_seven:
        return check_seven
    elif check_eight:
        return check_eight
    else:
        return False