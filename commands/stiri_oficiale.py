from bs4 import BeautifulSoup
import requests

from commands import formatters
from core import constants


def get_children(elements):
    return elements.find_all(True, recursive=False)


def parse_actualizat_la(element):
    return element.time.span.text.strip().replace(":", "")


def parse_header(time_and_who):
    date_time, author = get_children(time_and_who.div)
    date, time = [element.text.strip() for element in get_children(date_time)]
    return f"{date} {time}", author.text.strip()


def latest_article(**kwargs):
    resp = requests.get(constants.URLS["stiri-oficiale"])
    soup = BeautifulSoup(resp.text)

    stats = {}
    children = get_children(soup.article.div)
    if len(children) == 4:
        header, title, desc, link = children
    elif len(children) == 5:
        header, actualizat, title, desc, link = children
        stats["actualizat_la"] = parse_actualizat_la(actualizat)
    else:
        raise ValueError(f"Invalid number of elements in article: {children}")

    date_time, author = parse_header(header)

    stats.update(
        {
            "autor": author,
            "data": date_time,
            "titlu": title.text.strip(),
            "descriere": desc.text.strip(),
            "url": link.a["href"],
        }
    )
    if "json" in kwargs:
        return stats

    return formatters.parse_global(
        title=f"❗️{stats['title']}", stats=stats, items={}
    )
