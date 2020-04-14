import logging
import re

from bs4 import BeautifulSoup
import requests
from pymongo import UpdateOne

from core import database
from core.constants import COLLECTION, SLUG

from scrapers.formatters import camel_case_to_field
from scrapers.formatters import string_to_field


logger = logging.getLogger(__name__)


def set_multiple(countries, collection):
    collection = database.get_collection(collection)
    for country in countries:
        country["country"] = country.pop("country_other")
        for key, val in country.items():
            try:
                country[key] = int(val.replace(",", ""))
            except ValueError:
                pass
    return collection.bulk_write(
        [
            UpdateOne(
                {"country": country["country"]},
                update={"$set": country},
                upsert=True,
            )
            for country in countries
        ]
    )


class WorldometersClient:
    url = "https://www.worldometers.info/coronavirus/#countries"

    def __init__(self):
        self.data = None

    def _fetch(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, features="html.parser")
        self.data = soup
        return soup

    def sync(self):
        soup = self._fetch()

        top_stats = {
            string_to_field(x.h1.text.strip()): x.div.span.text.strip()
            for x in soup.find_all(id="maincounter-wrap")
        }
        top_stats["last_updated"] = soup.find(
            string=re.compile("Last updated: ")
        )

        db_stats = database.get_stats(
            COLLECTION["global"], slug=SLUG["global"]
        )
        if db_stats and top_stats.items() <= db_stats.items():
            logger.info("Global: No updates")
            return

        database.set_stats(
            top_stats, collection=COLLECTION["global"], slug=SLUG["global"]
        )
        logger.info("Global: Completed")
        return top_stats

    def sync_archive(self):
        if not self.data:
            self._fetch()

        soup = self.data
        selector = "table#main_table_countries_today"
        ths = [
            camel_case_to_field(x.text.strip().replace(",", "_"))
            for x in soup.select(f"{selector} > thead > tr > th")
        ][:8]
        rows = soup.select(f"{selector} > tbody > tr")

        countries = []
        for row in rows:
            data = [x.text for x in row.select("td")]
            if "total" not in data[0].lower():
                countries.append({ths[i]: data[i] for i in range(len(ths))})

        result = set_multiple(
            countries=countries, collection=COLLECTION["country"],
        )
        if not result.upserted_count and not result.modified_count:
            return logger.info("Countries: No updates")

        msg = "Completed"
        if result.upserted_count:
            msg += f" New: {result.upserted_count}"
        if result.modified_count:
            msg += f" Updated: {result.modified_count}"
        logger.info(msg)
