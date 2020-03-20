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


def no_message_handler(update):
    if update.inline_query and update.inline_query.query == 'covid-all-stats':
        return f"""
    🦠 Covid Stats
     ├ Total cazuri confirmate: {get_results(URLS['total'])}
     ├ Cazuri confirmate la nivel de județ: {get_results(URLS['per_county'])}
     ├ Persoane decedate: {get_results(URLS['dead'])}
     ├ Persoane în carantină: {get_results(URLS['quarantined'])}
     └ Persoane izolate: {get_results(URLS['isolated'])}
    """
    return 'No message'
