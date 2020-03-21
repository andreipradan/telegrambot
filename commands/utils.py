from datetime import datetime
import pytz

import requests

from core import database


def get_db_stats(url):
    head = requests.head(url)
    validate_response(head)
    head_etag = head.headers.get('ETag')
    db_etag = database.get_etag().get('value')
    if not all([head_etag, db_etag]):
        return False
    if head_etag == db_etag:
        return database.get_stats_by_slug(db_etag)


def get_date(date):
    utc_datetime = datetime.utcfromtimestamp(date / 1000).replace(tzinfo=pytz.utc)
    dt = utc_datetime.astimezone(pytz.timezone('Europe/Bucharest'))
    return dt.strftime('%H:%M:%S %d-%m-%Y')


def get_last_updated(data):
    try:
        latest = int(max([r['attributes']['EditDate'] for r in data]))
    except (ValueError, TypeError):
        return '<could not extract last updated>'

    return get_date(latest)


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')
