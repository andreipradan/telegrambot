import scrapers
from core import database, constants
from scrapers import formatters


def local_quick_stats():
    stats = database.get_stats()

    return formatters.parse_global(
        title="🔴 Cazuri noi", stats=stats, items={},
    )


def local_latest_article():
    stats = database.get_stats(slug=constants.SLUG["stiri-oficiale"])
    items = {stats.pop("descriere"): [stats.pop("url")]}
    return formatters.parse_global(
        title=f"🔵 {stats.pop('titlu')}", stats=stats, items=items, emoji="❗"
    )


def history():
    return "Historical data coming soon"


# TODO: replace this with db data
def global_():
    return scrapers.global_()
