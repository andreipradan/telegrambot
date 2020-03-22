RO_FIELDS = [
    "Cazuri_confirmate",
    "Persoane_decedate",
    "Persoane_vindecate",
    "Persoane_in_carantina",
    "Persoane_izolate",
    "Cazuri_infirmate",
    "Probe_in_asteptare",
    "EditDate",
]
COUNTY_FIELDS = RO_FIELDS + [
    "Judete",
    "Regiune_dezvoltare",
    "Populatie",
]

URLS = {
    'ROMANIA': ('https://services7.arcgis.com/I8e17MZtXFDX9vvT/arcgis/rest/'
                'services/Coronavirus_romania/FeatureServer/0/query'
                '?f=json&where=1%3D1&returnGeometry=false'
                f"&outFields={','.join(COUNTY_FIELDS)}"
                '&orderByFields=Cazuri_confirmate%20desc&resultOffset=0'
                '&resultRecordCount=42&cacheHint=true'),
    'GLOBAL': 'https://www.worldometers.info/coronavirus/#countries',
}

DEFAULT_DB = 'telegrambot_db'
COLLECTION = {
    'etag': 'etag',
    'romania': 'romania',
    'counties': 'counties',
}
SLUG = {
    'etag': 'etag_slug',
    'ro': 'Romania'
}
