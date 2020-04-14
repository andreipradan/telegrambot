import logging

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
    slug = SLUG["stiri-oficiale"]
    url = "https://stirioficiale.ro/informatii"

    def _fetch(self):
        resp = requests.get(self.url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, features="html.parser")

        stats = {}
        children = get_children(soup.article.div)
        if len(children) == 4:
            header, title, desc, link = children
        elif len(children) == 5:
            header, sub_header, title, desc, link = children
            key, value = parse_sub_header(sub_header)
            stats[key] = value
        else:
            raise ValueError(
                f"Invalid number of elements in article: {children}"
            )

        date_time, author = parse_header(header)

        stats.update(
            {
                "autor": author,
                "data": date_time,
                "titlu": parse_text(title),
                "descriere": parse_text(desc),
                "url": link.a["href"],
            }
        )
        return stats

    def sync(self):
        data = self._fetch()
        db_stats = database.get_stats(slug=SLUG["stiri-oficiale"])
        if db_stats and data.items() <= db_stats.items():
            logger.info("Stiri: No updates")
            return

        database.set_stats(
            stats=data,
            collection=COLLECTION["romania"],
            slug=SLUG["stiri-oficiale"],
        )
        logger.info("Stiri: Completed")
        return data
