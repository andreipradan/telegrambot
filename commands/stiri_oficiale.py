from bs4 import BeautifulSoup
import requests

from commands import formatters
from core import constants


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


def latest_article(**kwargs):
    resp = requests.get(constants.URLS["stiri-oficiale"])
    soup = BeautifulSoup(resp.text)

    stats = {}
    children = get_children(soup.article.div)
    if len(children) == 4:
        header, title, desc, link = children
    elif len(children) == 5:
        header, sub_header, title, desc, link = children
        key, value = parse_sub_header(sub_header)
        stats[key] = value
    else:
        raise ValueError(f"Invalid number of elements in article: {children}")

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
    if "json" in kwargs:
        return stats

    return formatters.parse_global(
        title=f"❗️{stats['title']}", stats=stats, items={}
    )
