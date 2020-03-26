ALLOWED_COMMANDS = {
    'analyze_sentiment',
    'start',
}
COMMANDS_WITH_TEXT = [
    'analyze_sentiment',
    'global_',
]
COMMANDS_WITH_UPDATE = [
    'start',
]

URLS = {
    'romania': 'https://services7.arcgis.com/I8e17MZtXFDX9vvT/arcgis/rest/'
               'services/Total_cazuri_confirmate/FeatureServer/0/query'
               '?f=json&where=1%3D1&outFields=*',
    'global': 'https://www.worldometers.info/coronavirus/#countries',
}

DEFAULT_DB = 'telegrambot_db'
COLLECTION = {
    'etag': 'etag-collection',
    'romania': 'romania-collection',
}
SLUG = {
    'etag': 'etag-slug',
    'romania': 'romania-slug',
}
