from core import database, constants
from scrapers import formatters


def prepare_items(title, data):
    items = {}
    for item in data:
        items[item.pop(title)] = item
    return items


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


def local_global_stats():
    top_stats = database.get_stats(
        collection=constants.COLLECTION["global"],
        slug=constants.SLUG["global"],
    )
    countries = list(
        database.get_many(
            constants.COLLECTION["country"], order_by="total_cases",
        )[:3]
    )
    for item in countries:
        del item["_id"]
    last_updated = top_stats.pop("last_updated")
    return formatters.parse_global(
        title="🌎 Global Stats",
        stats=top_stats,
        items=prepare_items("country", countries),
        emoji="🦠",
        footer=f"({last_updated})\n[Source: worldometers.info]",
    )
