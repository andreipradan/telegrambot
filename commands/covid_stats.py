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


def _validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f'Got an unexpected status code: {status_code}')


def get_results(url):
    response = requests.get(url)
    _validate_response(response)
    return response.json()['features'][0]['attributes']['value']


def get_covid_stats(update):
    return f"""
    🦠 Covid Stats
     ├ Confirmati: {get_results(URLS['total'])}
     ├ Decedati: {get_results(URLS['dead'])}
     ├ Carantinați: {get_results(URLS['quarantined'])}
     └ Izolați: {get_results(URLS['isolated'])}
    """


def get_county_details(county):
    return f"""
    🦠 {county['Judete']}
     ├ Populatie: {county['Populatie']}
     ├ Confirmați: {county['Cazuri_confirmate']}
     ├ Decedați: {county['Persoane_decedate']}
     ├ Carantinați: {county['Persoane_in_carantina']}
     ├ Izolați: {county['Persoane_in_carantina']}
     └ Vindecați: {county['Persoane_vindecate']}

    """


def get_covid_county_details(update):
    text = ' '.join(update.message.text.split(' ')[1:])
    if not text:
        return 'County name required'

    response = requests.get(URLS['per_county'])
    _validate_response(response)

    counties = response.json()['features']
    county = ''
    for feature in counties:
        county_details = feature['attributes']
        if county_details['Judete'] == text:
            county = county_details
    return get_county_details(county) if county else f"Available counties: {' | '.join(c['attributes']['Judete'] for c in counties)}"

def get_county_confirmed(county):
    return f"{county['Judete']}: {county['Cazuri_confirmate']}"


def get_covid_per_county(update):
    response = requests.get(URLS['per_county'])
    _validate_response(response)
    counties = response.json()['features']
    return '\t 🦠 '.join(
        get_county_confirmed(county['attributes'])
        for county in counties
    )
