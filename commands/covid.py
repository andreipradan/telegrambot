import re
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests

from core import constants, database
from commands import parsers
from commands import utils
from core.constants import COLLECTION, SLUG
from core.serializers import TotalSerializer
from core.utils import check_etag


def get_stats(url, serializer, **kwargs):
    source, stats = None, None
    if check_etag(url):
        db_stats = database.get_stats(
            collection=COLLECTION['romania'],
            slug=SLUG['romania']
        )
        if db_stats:
            stats = serializer(data=db_stats).data
            source = 'DB'

    # external request
    if not stats:
        stats = utils.request_total(url)
        source = 'API'

    if 'json' in kwargs:
        if isinstance(stats, dict):
            stats['Source'] = source
        return stats

    return parsers.parse_global(
        title=f'🦠 Romania',
        stats=stats,
        items={},
        footer=f'[Source {source}]'
    )


def total(**kwargs):
    return get_stats(
        url=constants.URLS['romania'],
        serializer=TotalSerializer,
        collection='romania',
        slug='romania',
        request_func=utils.request_total,
        **kwargs
    )


def global_(count=None):
    count = count.strip() if count else 5

    try:
        count = int(count)
    except ValueError:
        return f"""
        Invalid count: "{count}".
        Syntax: /global <count: Optional[int]>
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
    )
