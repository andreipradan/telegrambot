from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
import pytz
from pytz import utc

import requests

from core import database
from core import constants


def get_date(date):
    utc_datetime = datetime.utcfromtimestamp(date / 1000).replace(tzinfo=utc)
    dt = utc_datetime.astimezone(pytz.timezone('Europe/Bucharest'))
    return dt.strftime('%H:%M:%S %d-%m-%Y')


def get_db_stats(url, county=None):
    head = requests.head(url)
    validate_response(head)
    head_etag = head.headers.get('ETag')
    db_etag = database.get_etag().get('value')
    if not all([head_etag, db_etag]):
        return False
    if head_etag == db_etag:
        get_stats_kwargs = {
            'slug': constants.RO_SLUG
        } if county else {
            'collection': constants.COUNTY_COLLECTION,
            'slug': county
        }
        return database.get_stats(**get_stats_kwargs)


def get_last_updated(data):
    try:
        return int(max([r['attributes']['EditDate'] for r in data]))
    except (ValueError, TypeError):
        pass
    return '<could not extract last updated>'


def get_verbose(field):
    return ' '.join(field.split('_'))


def request_data():
    response = requests.get(constants.URLS['ROMANIA'])
    validate_response(response)
    return response.json()['features'], response.headers.get('ETag')


def request_judet(judet):
    counties, etag = request_data()
    county = None
    for feature in counties:
        county_details = feature['attributes']
        if county_details['Judete'] == judet:
            county = county_details

    if not county:
        available_counties = ' | '.join(
            county['attributes']['Judete'] for county in counties
        )
        return f"Available counties: {available_counties}"

    database.set_etag(etag)
    database.set_stats_for_slug(f"{county['Judete']}-{etag}", **county)
    return county


def request_romania():
    data, etag = request_data()
    ro = OrderedDict()
    ro['EditDate'] = get_last_updated(data)
    for field in constants.RO_FIELDS:
        ro[field] = sum([r['attributes'][field] for r in data])

    new = deepcopy(ro)
    old_version = database.get_stats('top_stats', constants.RO_SLUG)
    if old_version:
        for key in ro:
            new_value, old_value = ro[key], old_version.get(key)
            if new_value != old_value:
                diff = new_value - old_value if old_value else 0
                new[key] = f"{new_value} ({'+' if diff >= 0 else ''}{diff})"

    database.set_etag(etag)
    database.set_stats_for_slug(constants.RO_SLUG, **ro)
    database.set_multiple('judete', data)
    return new


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')
