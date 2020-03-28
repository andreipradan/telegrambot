from bs4 import BeautifulSoup
import requests

from commands import formatters
from core import constants


def get_children(elements):
    return elements.find_all(True, recursive=False)


def parse_header(time_and_who):
    date_time, author = get_children(time_and_who.div)
    date, time = [element.text.strip() for element in get_children(date_time)]
    return f"{date} {time}", author.text.strip()


def latest_article(**kwargs):
    resp = requests.get(constants.URLS["stiri-oficiale"])
    soup = BeautifulSoup(resp.text)

    header, title, desc, link = get_children(soup.article.div)
    date_time, author = parse_header(header)

    stats = {
        "author": author,
        "date_time": date_time,
        "title": title.text.strip(),
        "description": desc.text.strip(),
        "url": link.a["href"],
    }
    if "json" in kwargs:
        return stats

    return formatters.parse_global(
        title=f"❗️{stats['title']}", stats=stats, items={}
    )
