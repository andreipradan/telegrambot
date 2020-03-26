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
    'romania': 'https://api1.datelazi.ro/api/v2/data/ui-data/',
    'worldometers': 'https://www.worldometers.info/coronavirus/#countries',
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
