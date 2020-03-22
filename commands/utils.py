from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
import pytz
from pytz import utc

import requests

from core import database
from core import constants


def check_etag(url):
    head = requests.head(url)
    validate_response(head)
    head_etag = head.headers.get('ETag')

    db_etag = database.get_etag()
    if not db_etag:
        return False
    db_etag = db_etag.get('value')

    if not all([head_etag, db_etag]):
        return False

    return head_etag == db_etag


def get_date(date):
    utc_datetime = datetime.utcfromtimestamp(date / 1000).replace(tzinfo=utc)
    dt = utc_datetime.astimezone(pytz.timezone('Europe/Bucharest'))
    return dt.strftime('%H:%M:%S %d-%m-%Y')


def get_db_stats(url, county=None, many=False):
    if check_etag(url):
        if many:
            return database.get_all('counties')
        elif not county:
            return database.get_stats(
                collection=constants.COLLECTION['romania'],
                slug=constants.SLUG['romania'],
            )
        return database.get_stats(
            collection=constants.COLLECTION['counties'],
            slug=county
        )


def get_last_updated(data):
    try:
        return int(max([r['EditDate'] for r in data]))
    except (ValueError, TypeError):
        pass
    return '<could not extract last updated>'


def get_verbose(field):
    return ' '.join(field.split('_'))


def request_data():
    response = requests.get(constants.URLS['ROMANIA'])
    validate_response(response)
    feats = response.json()['features']
    return [item['attributes'] for item in feats], response.headers.get('ETag')


def request_counties():
    data, etag = request_data()

    ro = OrderedDict()
    ro['EditDate'] = get_last_updated(data)
    for field in constants.RO_FIELDS:
        ro[field] = sum([r[field] for r in data])

    database.set_etag(etag)
    database.set_stats(constants.SLUG['romania'], ro)
    database.set_multiple(data, constants.COLLECTION['counties'])

    return data


def request_judet(judet):
    counties, etag = request_data()
    county = None
    for feature in counties:
        county_details = feature
        if county_details['Judete'] == judet:
            county = county_details

    if not county:
        available_counties = ' | '.join(
            county['Judete'] for county in counties
        )
        return f"Available counties: {available_counties}"

    database.set_etag(etag)
    database.set_multiple(counties, constants.COLLECTION['counties'])
    return county


def request_romania():
    data, etag = request_data()
    ro = OrderedDict()
    ro['EditDate'] = get_last_updated(data)
    for field in constants.RO_FIELDS:
        ro[field] = sum([r[field] for r in data])

    new = deepcopy(ro)
    old_version = database.get_stats(constants.COLLECTION['romania'], constants.SLUG['romania'])
    if old_version:
        for key in ro:
            new_value, old_value = ro[key], old_version.get(key)
            if new_value != old_value:
                diff = new_value - old_value if old_value else 0
                new[key] = f"{new_value} ({'+' if diff >= 0 else ''}{diff})"

    database.set_etag(etag)
    database.set_stats(constants.SLUG['romania'], ro)
    database.set_multiple(data, constants.COLLECTION['counties'])
    return new


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')
