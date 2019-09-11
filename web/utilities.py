import re


##
# String validations
#
##
def check_existence(string, name):
    strErr = 'Error: please enter a' + name

    if not string:
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

def check_failed_validation(title, email, art):
    
    check_one = check_existence(title, ' title')
    check_two = check_existence(email, 'n email')
    
    check_three = check_strings(title, 'title')
    check_four = check_email(email)

    check_five = check_colors(art)

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
    else:
        return False