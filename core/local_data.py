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
    if not stats:
        return "Nu sunt statistici salvate pentru ziua de azi"
    stats = DLZSerializer.deserialize(stats)
    return formatters.parse_global(title="🔴 Cazuri noi", stats=stats, items={})


def local_latest_article():
    stats = database.get_stats(slug=SLUG["stiri-oficiale"])
    if not stats:
        return "Nu sunt stiri salvate pentru ziua de azi"
    items = {stats.pop("descriere"): [stats.pop("url")]}
    return formatters.parse_global(
        title=f"🔵 {stats.pop('titlu')}", stats=stats, items=items, emoji="❗"
    )


def datelazi():
    return "https://telegrambot.pradan.dev/"


def local_global_stats():
    top_stats = database.get_stats(
        collection=COLLECTION["global"], slug=SLUG["global"]
    )
    if not top_stats:
        return "Nu sunt statistici globale pentru ziua de azi"
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
    if not stats or not stats.get("Judete"):
        return "Nu sunt date despre județe pentru ziua de azi"
    deserialized = DLZArchiveSerializer.deserialize(stats)
    stats = deserialized["Judete"]
    counties = list(reversed(sorted(stats, key=stats.get)))

    max_key_len = len(counties[0])
    max_val_len = len(str(stats[counties[0]]))

    top_three = counties[:3]
    remaining = list(sorted(counties[3:]))
    return formatters.parse_global(
        title=f"🇷🇴Top cazuri confirmate",
        stats=[
            f"🦠 `{name:<{max_key_len}}: {stats[name]:<{max_val_len}}`"
            for name in top_three
        ],
        items=["\nRestul județelor"]
        + [
            " ".join(
                [
                    f"`{name:<{max_key_len}}: {stats[name]:<{max_val_len}}`"
                    for name in judete
                ]
            )
            for judete in chunks(remaining, 15)
        ],
        emoji="🦠",
        footer=f"\n`Actualizat la: {deserialized['Data']}`",
    )


def local_age():
    stats = database.get_stats(slug=SLUG["romania"])
    if not stats:
        return "Nu sunt statistici de vârstă pentru ziua de azi"
    serializer = DLZArchiveSerializer
    serializer.deserialize_fields = [
        f for f in serializer.deserialize_fields if f != "Data"
    ]
    deserialized = DLZArchiveSerializer.deserialize(stats)
    stats = deserialized["Categorii de vârstă"]
    categories = list(reversed(sorted(stats)))

    max_key_len = len(categories[0])
    max_val_len = len(str(stats[categories[0]]))
    return formatters.parse_global(
        title=f"🇷🇴Categorii de vârstă",
        stats=[
            f"🦠 `{k:<{max_key_len}}: {stats[k]:<{max_val_len}}`" for k in stats
        ],
        items=[],
        emoji="🦠",
        footer=f"\n`Actualizat la: {deserialized['Data']}`",
    )
