import re
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests

from core import constants
from commands import parsers


def global_(count=None):
    count = count.strip() if count else 3

    try:
        count = int(count)
    except ValueError:
        return f'Invalid count: "{count}".'

    main_stats_id = 'maincounter-wrap'

    soup = BeautifulSoup(requests.get(constants.URLS['worldometers']).text)

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
    )
