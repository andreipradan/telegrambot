FIELDS = [
    "Judete",
    "Cazuri_confirmate",
    # "Regiune_dezvoltare",
    # "Populatie",
    "Persoane_in_carantina",
    "Persoane_izolate",
    "Persoane_decedate",
    "Persoane_vindecate",
    "Probe_in_asteptare",
    "Cazuri_infirmate",
    "EditDate"
]

RO_URL = ('https://services7.arcgis.com/I8e17MZtXFDX9vvT/arcgis/rest/'
          'services/Coronavirus_romania/FeatureServer/0/query'
          '?f=json&where=1%3D1&returnGeometry=false'
          f"&outFields={','.join(FIELDS)}"
          '&orderByFields=Cazuri_confirmate%20desc&resultOffset=0'
          '&resultRecordCount=42&cacheHint=true')

URLS = {
    'romania': f'{RO_URL}',
    'global': 'https://www.worldometers.info/coronavirus/#countries',
}
