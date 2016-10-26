import json
from flask import make_response


def datetimeformat(value, format='%b %d, %Y'):
    return value.strftime(format)


def make_json_response(value, code=401):
    response = make_response(json.dumps(value), code)
    response.headers['Content-Type'] = 'application/json'
    return response
