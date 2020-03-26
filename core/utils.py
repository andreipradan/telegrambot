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
