import logging

import feedparser
import requests
from bs4 import BeautifulSoup

from core import database
from core.constants import SLUG, COLLECTION

logger = logging.getLogger(__name__)


def get_children(elements):
    return elements.find_all(True, recursive=False)


def parse_text(element):
    return element.text.strip()


def parse_sub_header(element):
    key, *value = get_children(element.time)
    key = parse_text(key).replace(":", "")
    date, time, *_ = value
    return key, f"{parse_text(date)} {parse_text(time)}"


def parse_header(time_and_who):
    date_time, author = get_children(time_and_who.div)
    date, time = [parse_text(element) for element in get_children(date_time)]
    return f"{date} {time}", parse_text(author)


class StiriOficialeClient:
    base_url = "https://stirioficiale.ro/"
    slug = SLUG["stiri-oficiale"]
    url = base_url + "feeds/informatii.xml"

    @classmethod
    def _fetch_feed(cls):
        feed = feedparser.parse(cls.url)
        if not feed.entries:
            logger.error("Stiri: No entries on the feed")
            return
        latest = feed.entries[0]
        return {
            "autor": latest["author"],
            "data": latest["published"][5:22],
            "titlu": latest["title"],
            "descriere": BeautifulSoup(
                latest["summary"], features="html.parser"
            ).text.strip(),
            "url": latest["link"],
        }

    @classmethod
    def _get_new_etag(cls):
        local_etag = database.get_stats("etags", location="stiri-oficiale")
        etag_response = requests.head(cls.base_url)
        etag_response.raise_for_status()
        etag = etag_response.headers["ETag"]
        if not local_etag or local_etag["value"] != etag:
            return etag

    @classmethod
    def sync(cls):
        new_etag = cls._get_new_etag()
        if not new_etag:
            logger.info("Stiri: No updates (same etag)")
            return

        data = cls._fetch_feed()
        if not data:
            logger.info("Stiri: No entries on the feed")
            return
        database.set_stats(
            stats=data,
            collection=COLLECTION["romania"],
            slug=SLUG["stiri-oficiale"],
        )
        database.set_stats(
            {"value": new_etag}, "etags", location="stiri-oficiale"
        )
        logger.info("Stiri: Completed")
        return data
