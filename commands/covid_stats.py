import re
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests

from commands.utils import get_records_from_db, parse_country
from core.database import get_collection

base_url = (
    'https://services7.arcgis.com/I8e17MZtXFDX9vvT/arcgis/rest/services/'
    'Coronavirus_romania/FeatureServer/0/query?f=json&where=1%3D1&'
    'returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*'
)
count_base_url = (
    f'{base_url}&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22'
    'onStatisticField%22%3A%22'
)
suffix = '%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&cacheHint=true'

URLS = {
    'total': f'{count_base_url}Cazuri_confirmate{suffix}',
    'per_county': (
        f'{base_url}&orderByFields=Cazuri_confirmate%20desc&resultOffset=0&'
        'resultRecordCount=42&cacheHint=true'
    ),
    'dead': f'{count_base_url}Persoane_decedate{suffix}',
    'quarantined': f'{count_base_url}Persoane_in_carantina{suffix}',
    'isolated': f'{count_base_url}Persoane_izolate{suffix}',
    'global': 'https://www.worldometers.info/coronavirus/#countries',
}


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')


def get_results(field):
    url = URLS[field]
    response = requests.get(url)
    validate_response(response)
    return response.json()['features'][0]['attributes']['value']


def get_covid_stats():
    return f"""
    🦠 Covid Stats
     ├ Confirmati: {get_results('total')}
     ├ Decedati: {get_results('dead')}
     ├ Carantinați: {get_results('quarantined')}
     └ Izolați: {get_results('isolated')}
    """


def get_covid_county_details(text):
    if not text:
        return 'Syntax: /covid_county_details <County name>'

    response = requests.get(URLS['per_county'])
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
    response = requests.get(URLS['per_county'])
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

    url = URLS['global']
    # head_response = requests.head(url)
    # if not head_response.status_code == 200:
    #     return f'Bad Status code: {head_response.status_code}'
    #
    # collection = get_collection('etags')
    # etag = head_response.headers['ETag']
    # if etag == collection.find_one({'id': 1})['ETag']:
    #     return get_records_from_db(collection)
    #
    # collection.update_one(
    #     {'id': 1},
    #     update={'$set': {'ETag': etag}},
    #     upsert=True,
    # )

    main_stats_id = 'maincounter-wrap'

    soup = BeautifulSoup(requests.get(url).text)
    last_updated_string = soup.find(string=re.compile('Last updated: '))

    cases, deaths, recovered = [
        (x.h1.text, x.div.span.text.strip())
        for x in soup.find_all(id=main_stats_id)
    ]

    ths = [x.text for x in
           soup.select('table#main_table_countries_today > thead > tr > th')][
          1:6
          ]
    rows = soup.select('table#main_table_countries_today > tbody > tr')[:count]

    countries = OrderedDict()
    for row in rows:
        data = [x.text for x in row.select('td')]
        country = data.pop(0)
        countries[country] = {}
        for i, value in enumerate(ths):
            countries[country][ths[i]] = data[i]
        # results.append({ths[i]: data[i] for i in range(len(ths))})
    per_country = '\n'.join(
        [
            f"""
🦠 {country}:
    {parse_country(stats)}
    """ for country, stats in countries.items()
        ]
    )
    return f"""
    Covid Global Stats ({last_updated_string})
{cases[0]}  {cases[1]}
{deaths[0]}                 {deaths[1]}
{recovered[0]}          {recovered[1]}

{per_country}
    """
