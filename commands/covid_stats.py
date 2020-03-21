from datetime import datetime
import pytz
import re
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests

from commands.constants import URLS
from commands.parsers import parse_details
from commands.parsers import parse_global
from core import database

delimiter = '=========================='


def check_etag(url):
    head = requests.head(url)
    if head.status_code != 200:
        return f'Failed to pull data. Status code: {head.status_code}'
    head_etag = head.headers.get('ETag')
    db_etag = database.get_etag().get('value')
    if not all([head_etag, db_etag]):
        return False
    return head_etag == db_etag


def request_romania():
    response = requests.get(URLS['ROMANIA'])
    validate_response(response)
    data = response.json()['features']
    ro = OrderedDict()
    ro['Confirmati'] = sum([r['attributes']['Cazuri_confirmate'] for r in data])
    ro['Decedati'] = sum([r['attributes']['Persoane_decedate'] for r in data])
    ro['Carantinati'] = sum([r['attributes']['Persoane_izolate'] for r in data])
    ro['Izolati'] = sum([r['attributes']['Persoane_izolate'] for r in data])

    last_updated = get_last_updated(data)
    database.set_etag(response.headers.get('ETag'))
    database.set_romania_stats(
        **ro,
        last_updated=last_updated,
    )

    return f"""
{delimiter}
🦠 Romania Covid Updates
{parse_details(ro)}
{delimiter}
 Last updated: {last_updated}
 [Source: API]
{delimiter}
"""


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')


def get_last_updated(data):
    try:
        latest = int(max([r['attributes']['EditDate'] for r in data])) / 1000
    except (ValueError, TypeError):
        return '<could not extract last updated>'

    utc_datetime = datetime.utcfromtimestamp(latest).replace(tzinfo=pytz.utc)
    dt = utc_datetime.astimezone(pytz.timezone('Europe/Bucharest'))
    return dt.strftime('%H:%M:%S %d-%m-%Y')


def get_romania_stats():
    db_stats = (
        database.get_romania_stats()
        if check_etag(URLS['ROMANIA'])
        else None
    )

    if db_stats:
        last_updated = db_stats.pop('last_updated')
        db_stats.pop('_id', None)
        db_stats.pop('slug', None)
        return parse_global(
            title=f'{delimiter}\n🦠 Romania Stats',
            top_stats=db_stats,
            items={},
            footer=f'Last updated: {last_updated}\n[Source: DB]\n{delimiter}'
        )

    return request_romania()


def get_covid_county_details(text):
    if not text:
        return 'Syntax: /covid_county_details <County name>'

    response = requests.get(URLS['ROMANIA'])
    validate_response(response)

    counties = response.json()['features']
    county = None
    for feature in counties:
        county_details = feature['attributes']
        if county_details['Judete'] == text:
            county = county_details

    if not county:
        available_counties = ' | '.join(
            county['attributes']['Judete'] for county in counties
        )
        return f"Available counties: {available_counties}"

    return f"""
🦠 {county['Judete']}
 ├ Populatie: {county['Populatie']}
 ├ Confirmați: {county['Cazuri_confirmate']}
 ├ Decedați: {county['Persoane_decedate']}
 ├ Carantinați: {county['Persoane_in_carantina']}
 ├ Izolați: {county['Persoane_in_carantina']}
 └ Vindecați: {county['Persoane_vindecate']}

Last updated: {get_last_updated(counties)}
    """


def get_covid_counties():
    response = requests.get(URLS['ROMANIA'])
    validate_response(response)
    counties = response.json()['features']
    return '\t 🦠 '.join(
        f"{county['attributes']['Judete']}: "
        f"{county['attributes']['Cazuri_confirmate']}"
        for county in counties
    )


def get_covid_global(count=None):
    count = count.strip() if count else 5

    try:
        count = int(count)
    except ValueError:
        return f"""
        Invalid count: "{count}".
        Syntax: /covid_global <count: Optional[int]>
        """

    main_stats_id = 'maincounter-wrap'

    soup = BeautifulSoup(requests.get(URLS['GLOBAL']).text)

    top_stats = {
        x.h1.text: x.div.span.text.strip()
        for x in soup.find_all(id=main_stats_id)
    }

    selector = 'table#main_table_countries_today'
    ths = [x.text for x in soup.select(f'{selector} > thead > tr > th')][1:6]
    rows = soup.select(f'{selector} > tbody > tr')[:count]

    countries = {}
    for row in rows:
        data = [x.text for x in row.select('td')]
        country = data.pop(0)
        countries[country] = OrderedDict()
        for i, value in enumerate(ths):
            countries[country][ths[i]] = data[i]

    last_updated = soup.find(string=re.compile('Last updated: '))
    return parse_global(
        title=f'{delimiter}======\n🌎 Global Stats',
        top_stats=top_stats,
        items=countries,
        item_emoji='🦠',
        footer=f"({last_updated})\n[Source: worldometers.info]"
               f"\n{delimiter}======"
    )
