import re

def check_username(username):
    username_reg = re.compile('^[a-zA-Z0-9_-]{3,20}$')
    v = username_reg.match(username)

    if username == None or v == None:
        return 'Invalid username'

def check_email(email):
    email_reg = re.compile('^[\S]+@[\S]+.[\S]+$')
    v = email_reg.match(email)

    if v == None:
        return 'Invalid e-mail'

def check_verify(password, verify):
    if password != verify:
        return 'Passwords do not match.'

def check_password(password):
    password_reg = re.compile('^.{3,20}$')
    v = password_reg.match(password)

    if v == None:
        return 'Password must be between 3 and 20 characters.'

def validate_subject_and_content(subject, content):
    errors = []

    if not subject:
        errors.append('Your blog post must have a subject.')
    if not content:
        errors.append('Your blog post must have content.')

    return errors

def check_errors(params):
    errors = {}
    error_username = check_username(params.get('username'))
    error_password = check_password(params.get('password'))
    error_email = check_email(params.get('email'))

    if error_username:
        errors['username'] = error_username

    if error_password:
        errors['password'] = error_password
    else:
        error_verify = check_verify(params.get('password'), params.get('verify'))
        if error_verify:
            errors['verify'] = error_verify

    if error_email:
        errors['email'] = error_email

    return errors
