import re
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests

from commands.constants import URLS
from commands.utils import parse_global
from core.database import get_collection


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')


def get_covid_stats():
    response = requests.get(URLS['ROMANIA'])
    validate_response(response)
    data = response.json()['features']
    return f"""
    🦠 Covid Stats
     ├ Confirmati: {sum([r['attributes']['Cazuri_confirmate'] for r in data])}
     ├ Decedati: {sum([r['attributes']['Persoane_decedate'] for r in data])}
     ├ Carantinați: {sum([r['attributes']['Persoane_izolate'] for r in data])}
     └ Izolați: {sum([r['attributes']['Persoane_izolate'] for r in data])}
    """


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

    """


def get_covid_per_county():
    response = requests.get(URLS['ROMANIA'])
    validate_response(response)
    counties = response.json()['features']
    return '\t 🦠 '.join(
        f"{county['attributes']['Judete']}: "
        f"{county['attributes']['Cazuri_confirmate']}"
        for county in counties
    )


def get_covid_global(count=None):
    count = count.strip() or 5

    try:
        count = int(count)
    except ValueError:
        return f"""
        Invalid count: "{count}".
        Syntax: /covid_global <count: Optional[int]>
        """

    url = URLS['GLOBAL']
    head_response = requests.head(url)
    if not head_response.status_code == 200:
        return f'Bad Status code: {head_response.status_code}'

    collection = get_collection('etags')
    etag = head_response.headers['ETag']
    db_etag = collection.find_one({'id': 1})
    if db_etag and etag == db_etag['ETag']:
        top_stats = get_collection('top_stats').find_one({'id': 1})
        countries = get_collection('countries').find().sort({'TotalCases': -1})
        return parse_global(top_stats, countries, from_db=True)

    collection.update_one(
        {'id': 1},
        update={'$set': {'ETag': etag}},
        upsert=True,
    )

    main_stats_id = 'maincounter-wrap'

    soup = BeautifulSoup(requests.get(url).text)

    top_stats = {
        x.h1.text: x.div.span.text.strip()
        for x in soup.find_all(id=main_stats_id)
    }
    top_stats['last_updated'] = soup.find(string=re.compile('Last updated: '))
    get_collection('top_stats').update_one(
        {'id': 1},
        update={'$set': top_stats},
        upsert=True,
    )

    selector = 'table#main_table_countries_today'
    ths = [x.text for x in soup.select(f'{selector} > thead > tr > th')][1:6]
    rows = soup.select(f'{selector} > tbody > tr')[:count]

    countries = OrderedDict()
    for row in rows:
        data = [x.text for x in row.select('td')]
        country = data.pop(0)
        countries[country] = {}
        for i, value in enumerate(ths):
            countries[country][ths[i]] = data[i]

    for country_name, data in countries.items():
        get_collection('countries').update_one(
            {'slug': country_name},
            update={'$set': data},
            upsert=True
        )

    return parse_global(top_stats, countries)
