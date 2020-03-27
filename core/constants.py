ALLOWED_COMMANDS = {
    'analyze_sentiment',
    'start',
}
COMMANDS_FOR_VIEWS = [
    'latest_article',
    'histogram',
    'analyze_sentiment',
    'global_',
]
COMMANDS_WITH_TEXT = [
    'analyze_sentiment',
    'global_',
]
COMMANDS_WITH_UPDATE = [
    'start',
]

URLS = {
    'romania': 'https://api1.datelazi.ro/api/v2/data/ui-data/',
    'stiri-oficiale': 'https://stirioficiale.ro/informatii',
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
    'stiri-oficiale': 'stiri-oficiale-slug'
}

IDS = {
    'ap': 412945234,
    'covid-updates': -1001181792063,
    'pbs': -382272798,
}
