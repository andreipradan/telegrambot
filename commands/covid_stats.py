
import re
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests

from core import constants
from commands import parsers
from commands import utils
from core.serializers import CountrySerializer
from core.serializers import CountySerializer


def get_stats(serializer, request_func=None, **kwargs):
    if 'text' in kwargs and not kwargs['text']:
        return 'Syntax: /covid_county_details <County name>'

    county = kwargs.pop('text', None)
    stats = utils.get_db_stats(
        constants.URLS[constants.RO_SLUG],
        county=county
    )
    if stats:
        stats = serializer(data=stats).data
        source = 'DB'
    else:
        county_kwargs = {'judet': county} if county else {}
        stats = request_func(**county_kwargs)
        source = 'API'

    if 'json' in kwargs:
        stats['Source'] = source
        return stats

    last_updated = utils.get_date(stats.pop('EditDate'))
    return parsers.parse_global(
        title=f"🦠 {'Romania' if not county else 'Judetul ' + county}",
        stats=stats,
        items={},
        footer=f'Last updated: {last_updated}\n[Source {source}]'
    )


def get_romania_stats(**kwargs):
    return get_stats(CountrySerializer, utils.request_romania, **kwargs)


def get_county_details(**kwargs):
    return get_stats(CountySerializer, utils.request_judet, **kwargs)


def get_covid_counties():
    response = requests.get(constants.URLS['ROMANIA'])
    utils.validate_response(response)
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

    soup = BeautifulSoup(requests.get(constants.URLS['GLOBAL']).text)

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
    return parsers.parse_global(
        title=f'🌎 Global Stats',
        stats=top_stats,
        items=countries,
        emoji='🦠',
        footer=f"({last_updated})\n[Source: worldometers.info]",
        bar_length=32
    )
