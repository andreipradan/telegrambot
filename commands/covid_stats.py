from datetime import datetime

from flask import session
import requests

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
}


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')


def get_results(field):
    url = URLS[field]

    head_response = requests.head(url)

    last_modified = head_response.headers['Last-Modified']
    if last_modified == session.get(f'{field}_last_modified'):
        return session[f'{field}_value'], True

    response = requests.get(url)
    validate_response(response)
    value = response.json()['features'][0]['attributes']['value']

    session.update(
        {
            f'{field}_value': value,
            f'{field}_last_modified': last_modified,
        }
    )
    return value, False


def get_covid_stats():
    total, total_hit = get_results('total')
    dead, dead_hit = get_results('dead')
    quarantined, quarantined_hit = get_results('quarantined')
    isolated, isolated_hit = get_results('isolated')

    return f"""
    🦠 Covid Stats
     ├ Confirmati: {total}           {'H' if total_hit else 'M'}(Last update: {session.get('total_last_modified')})
     ├ Decedati: {dead}              {'H' if dead_hit else 'M'}(Last update: {session.get('dead_last_modified')})
     ├ Carantinați: {quarantined}    {'H' if quarantined_hit else 'M'}(Last update: {session.get('quarantined_last_modified')})
     └ Izolați: {isolated}           {'H' if isolated_hit else 'M'}(Last update: {session.get('isolated_last_modified')})

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
