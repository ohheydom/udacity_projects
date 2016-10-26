import re


def validate_field(val, field):
    if not val:
        return '{} is missing.'.format(field)


def validate_url(url, column):
    if url:
        reg = re.compile('^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$')
        v = reg.match(url)
        if v == None:
            return 'Invalid {}'.format(column)


def check_errors(name, description, link, careers_link):
    errors = {}
    error_name = validate_field(name, 'Company name')
    error_description = validate_field(description, 'Description')
    error_link = validate_url(link, 'link.')
    error_careers_link = validate_url(careers_link, 'careers link.')

    if error_name:
        errors['name'] = error_name
    if error_description:
        errors['description'] = error_description
    if error_link:
        errors['link'] = error_link
    if error_careers_link:
        errors['careers_link'] = error_careers_link

    return errors
