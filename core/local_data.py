from core import database
from core.constants import COLLECTION
from core.constants import SLUG
from core.utils import chunks
from scrapers import formatters
from serializers import DLZSerializer
from serializers import DLZArchiveSerializer


def prepare_items(title, data):
    items = {}
    for item in data:
        items[item.pop(title)] = item
    return items


def local_quick_stats():
    stats = database.get_stats(slug=SLUG["romania"])
    stats = DLZSerializer.deserialize(stats)
    return formatters.parse_global(
        title="🔴 Cazuri noi", stats=stats, items={},
    )


def local_latest_article():
    stats = database.get_stats(slug=SLUG["stiri-oficiale"])
    items = {stats.pop("descriere"): [stats.pop("url")]}
    return formatters.parse_global(
        title=f"🔵 {stats.pop('titlu')}", stats=stats, items=items, emoji="❗"
    )


def datelazi():
    return "https://datelazi.ro"


def local_global_stats():
    top_stats = database.get_stats(
        collection=COLLECTION["global"], slug=SLUG["global"],
    )
    countries = list(
        database.get_many(COLLECTION["country"], order_by="total_cases")[:3]
    )
    for item in countries:
        del item["_id"]
    last_updated = top_stats.pop("last_updated")
    return formatters.parse_global(
        title="🌎 Global Stats",
        stats=top_stats,
        items=prepare_items("country", countries),
        emoji="🦠",
        footer=f"\n`{last_updated}`\n[Source: worldometers.info](https://worldometers.info/)",
    )


def local_counties():
    stats = database.get_stats(slug=SLUG["romania"])
    if not stats.get("Judete"):
        return "Nu sunt date pentru ziua de astăzi"
    serializer = DLZArchiveSerializer
    serializer.deserialize_fields = [
        f for f in serializer.deserialize_fields if f != "Data"
    ]
    stats = DLZArchiveSerializer.deserialize(stats)["Judete"]
    counties = list(reversed(sorted(stats, key=stats.get)))

    max_key_len = len(counties[0])
    max_val_len = len(str(stats[counties[0]]))
    return formatters.parse_global(
        title=f"🇷🇴Top cazuri confirmate",
        stats=[
            f"🦠 `{name:<{max_key_len}}: {stats[name]:<{max_val_len}}`"
            for name in counties[:3]
        ],
        items=["\nRestul județelor"]
        + [
            " ".join(
                [
                    f"`{name:<{max_key_len}}: {stats[name]:<{max_val_len}}`"
                    for name in judete
                ]
            )
            for judete in chunks(counties[3:], 5)
        ],
        emoji="🦠",
    )


def local_age():
    stats = database.get_stats(slug=SLUG["romania"])
    serializer = DLZArchiveSerializer
    serializer.deserialize_fields = [
        f for f in serializer.deserialize_fields if f != "Data"
    ]
    stats = DLZArchiveSerializer.deserialize(stats)["Categorii de vârstă"]
    categories = list(reversed(sorted(stats)))  # , key=stats.get)))

    max_key_len = len(categories[0])
    max_val_len = len(str(stats[categories[0]]))
    return formatters.parse_global(
        title=f"🇷🇴Categorii de vârstă",
        stats=[
            f"🦠 `{k:<{max_key_len}}: {stats[k]:<{max_val_len}}`" for k in stats
        ],
        items=[],
        emoji="🦠",
    )
