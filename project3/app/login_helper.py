import hmac
import string
import random
import hashlib

SECRET = '?e@7[!{+w$)W<s4Z)ENTzfWZ-K#fK.LR'

# Hashing helper methods
def build_salt(length=5):
    return ''.join(random.choice(string.letters) for _ in xrange(length))

def build_password_hash(username, password, salt=None):
    if not salt:
        salt = build_salt()
    h = hashlib.sha256(username + password + salt).hexdigest()
    return '{},{}'.format(salt, h)

def valid_password(username, password, h):
    salt = h.split(',')[0]
    return h == build_password_hash(username, password, salt)

# Cookie helper methods
def build_secure_val(val):
    return '{}|{}'.format(val, hmac.new(SECRET, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if build_secure_val(val) == secure_val:
        return val
