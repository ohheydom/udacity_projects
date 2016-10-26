import random
import re
import string
import unicodedata


def slugify(value):
    value = unicodedata.normalize('NFKD', unicode(value)) \
            .encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def secret_key_generator(length):
    return ''.join([random.choice(string.ascii_letters + string.digits) \
        for _ in range(length)])

