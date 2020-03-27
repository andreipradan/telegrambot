from copy import deepcopy

import requests

from core import database
from core import validators


def check_etag(url):
    head = requests.head(url)
    validators.validate_response(head)
    head_etag = head.headers.get('ETag')

    db_etag = database.get_etag()
    if not db_etag:
        return False
    db_etag = db_etag.get('value')

    if not all([head_etag, db_etag]):
        return False

    return head_etag == db_etag


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def parse_diff(data, old_version):
    if not old_version:
        return data
    new = deepcopy(data)
    for key in data:
        new_value, old_value = data[key], old_version.get(key)
        if new_value != old_value:
            diff = new_value - old_value if old_value else 0
            new[key] = f"{new_value} ({'+' if diff >= 0 else ''}{diff})"
    return new


def parse_name(user):
    full_name = f'{user.first_name or ""} {user.last_name or ""}'
    return full_name if full_name.strip() else user.username


def parse_sentiment(data):
    if isinstance(data, str):
        return data
    score = data['Overall score']
    if score < 0:
        return 'Why so negative?'
    elif score > 0:
        return 'Nice to see you positive like that!'
    return 'You nailed it! You don\'t see everyday a neutral attitude.'
