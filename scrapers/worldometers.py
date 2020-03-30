import re
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests

from core import constants
from scrapers import formatters


def global_(text=None, **kwargs):
    text = text.strip() if text and isinstance(text, str) else 3

    try:
        text = int(text)
    except ValueError:
        return f'Invalid count: "{text}".'

    response = requests.get(constants.URLS["worldometers"])
    soup = BeautifulSoup(response.text, features="html.parser")

    top_stats = {
        formatters.string_to_field(x.h1.text.strip()): x.div.span.text.strip()
        for x in soup.find_all(id="maincounter-wrap")
    }

    selector = "table#main_table_countries_today"
    ths = [x.text for x in soup.select(f"{selector} > thead > tr > th")][1:6]
    rows = soup.select(f"{selector} > tbody > tr")[:text]

    countries = {}
    for row in rows:
        data = [x.text for x in row.select("td")]
        country = data.pop(0)
        countries[country] = OrderedDict()
        for i, value in enumerate(ths):
            countries[country][ths[i]] = data[i]

    last_updated = soup.find(string=re.compile("Last updated: "))
    if "json" in kwargs:
        top_stats["last_updated"] = last_updated
        return {"top_stats": top_stats, "countries": countries}
    return formatters.parse_global(
        title="🌎 Global Stats",
        stats=top_stats,
        items=countries,
        emoji="🦠",
        footer=f"({last_updated})\n[Source: worldometers.info]",
    )
