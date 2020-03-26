from copy import deepcopy
from datetime import datetime

import pytz
import requests

from core import database
from core import constants
from core.validators import validate_response


def get_last_updated(data):
    try:
        return int(max([r['EditDate'] for r in data]))
    except (ValueError, TypeError):
        pass
    return '<could not extract last updated>'


def request_data(url):
    response = requests.get(url)
    validate_response(response)
    json = response.json()
    error = json.get('error')
    if error:
        raise ValueError(error)
    feats = response.json()['features']
    return [item['attributes'] for item in feats], response.headers.get('ETag')


def request_total(url):
    data, etag = request_data(url)
    old_version = database.get_stats(constants.COLLECTION['romania'],
                                     constants.SLUG['romania'])
    data = data[0]
    data = {
        'Cazuri_confirmate': data['Cazuri_confirmate'],
        'Decedati': data['Decedati'],
        'Last updated': datetime.utcnow().astimezone(
            pytz.timezone('Europe/Bucharest')
        ).strftime('%H:%M:%S %d-%m-%Y %Z'),
    }
    new = deepcopy(data)
    if old_version:
        for key in data:
            new_value, old_value = data[key], old_version.get(key)
            if new_value != old_value:
                diff = new_value - old_value if old_value else 0
                new[key] = f"{new_value} ({'+' if diff >= 0 else ''}{diff})"

    database.set_etag(etag)
    database.set_stats(
        collection=constants.COLLECTION['romania'],
        slug=constants.SLUG['romania'],
        stats=data,
    )
    return new

