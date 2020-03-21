
import re
from collections import OrderedDict
from copy import deepcopy

from bs4 import BeautifulSoup
import requests

from core.constants import ROMANIA_STATS_SLUG, COUNTY_SLUG
from core.constants import URLS
from commands.parsers import parse_details
from commands.parsers import parse_global
from commands.utils import get_db_stats, get_date
from commands.utils import get_last_updated
from commands.utils import validate_response
from core import database

delimiter = '=========================='


def request_romania():
    response = requests.get(URLS['ROMANIA'])
    validate_response(response)
    data = response.json()['features']
    ro = OrderedDict()
    ro['Confirmati'] = sum([r['attributes']['Cazuri_confirmate'] for r in data])
    ro['Decedati'] = sum([r['attributes']['Persoane_decedate'] for r in data])
    ro['Carantinati'] = sum([r['attributes']['Persoane_in_carantina'] for r in data])
    ro['Izolati'] = sum([r['attributes']['Persoane_izolate'] for r in data])

    last_updated = get_last_updated(data)
    new_last_updated = last_updated
    new = deepcopy(ro)
    old_version = database.get_stats_by_slug(ROMANIA_STATS_SLUG)
    if last_updated != old_version['last_updated']:
        new_last_updated = (f"{last_updated}\n"
                            f"({old_version['last_updated']})")
    for key in ro:
        if ro[key] != old_version[key]:
            diff = ro[key] - old_version.get(key)
            new[key] = f"{ro[key]} ({'+' if diff >= 0 else ''}{diff})"

    database.set_etag(response.headers.get('ETag'))
    database.set_stats_for_slug(
        ROMANIA_STATS_SLUG,
        **ro,
        last_updated=last_updated,
    )

    return f"""
{delimiter}
🦠 Romania
{parse_details(new)}
{delimiter}
Last updated: {new_last_updated}
[Source: API]
{delimiter}
"""


def get_romania_stats():
    db_stats = (
        database.get_stats_by_slug(ROMANIA_STATS_SLUG)
        if get_db_stats(URLS['ROMANIA'], ROMANIA_STATS_SLUG)
        else None
    )

    if db_stats:
        last_updated = db_stats.pop('last_updated')
        db_stats.pop('_id', None)
        db_stats.pop('slug', None)
        return parse_global(
            title=f'{delimiter}\n🦠 Romania',
            top_stats=db_stats,
            items={},
            footer=f'Last updated: {last_updated}\n[Source: DB]\n{delimiter}'
        )

    return request_romania()


def get_county_details(text):
    if not text:
        return 'Syntax: /covid_county_details <County name>'

    db_stats = get_db_stats(URLS['ROMANIA'])
    if db_stats:
        last_updated = db_stats.pop('last_updated')
        db_stats.pop('_id', None)
        db_stats.pop('OBJECTID', None)
        db_stats.pop('slug', None)
        return parse_global(
            title=f'{delimiter}\n🦠 {db_stats.pop("Judete")}',
            top_stats=db_stats,
            items={},
            footer=f'Last updated: {last_updated}\n[Source: DB]\n{delimiter}'
        )

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

    last_updated = get_date(county.pop('EditDate'))
    database.set_etag(response.headers.get('ETag'))
    database.set_stats_for_slug(
        response.headers['ETag'],
        **county,
        last_updated=last_updated,
    )

    return f"""
{delimiter}
🦠 {county['Judete']}
 ├ Populatie: {county['Populatie']}
 ├ Confirmați: {county['Cazuri_confirmate']}
 ├ Decedați: {county['Persoane_decedate']}
 ├ Carantinați: {county['Persoane_in_carantina']}
 ├ Izolați: {county['Persoane_in_carantina']}
 └ Vindecați: {county['Persoane_vindecate']}

Last updated: {last_updated}
[Source: API]
{delimiter}
    """


def get_covid_counties():
    response = requests.get(URLS['ROMANIA'])
    validate_response(response)
    counties = response.json()['features']
    return '\t 🦠 '.join(
        f"{county['attributes']['Judete']}: "
        f"{county['attributes']['Cazuri_confirmate']}"
        for county in counties
    )


def get_covid_global(count=None):
    count = count.strip() if count else 5

    try:
        count = int(count)
    except ValueError:
        return f"""
        Invalid count: "{count}".
        Syntax: /covid_global <count: Optional[int]>
        """

    main_stats_id = 'maincounter-wrap'

    soup = BeautifulSoup(requests.get(URLS['GLOBAL']).text)

    top_stats = {
        x.h1.text: x.div.span.text.strip()
        for x in soup.find_all(id=main_stats_id)
    }

    selector = 'table#main_table_countries_today'
    ths = [x.text for x in soup.select(f'{selector} > thead > tr > th')][1:6]
    rows = soup.select(f'{selector} > tbody > tr')[:count]

    countries = {}
    for row in rows:
        data = [x.text for x in row.select('td')]
        country = data.pop(0)
        countries[country] = OrderedDict()
        for i, value in enumerate(ths):
            countries[country][ths[i]] = data[i]

    last_updated = soup.find(string=re.compile('Last updated: '))
    return parse_global(
        title=f'{delimiter}======\n🌎 Global Stats',
        top_stats=top_stats,
        items=countries,
        item_emoji='🦠',
        footer=f"({last_updated})\n[Source: worldometers.info]"
               f"\n{delimiter}======"
    )
