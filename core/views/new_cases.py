import logging
import os

import requests
import telegram
from flask import Blueprint
from flask import abort

import scrapers
from core.constants import COLLECTION
from core.constants import SLUG
from core.constants import TOKEN
from scrapers import formatters
from core import database
from core import utils
from serializers import DLZSerializer
from serializers import DLZArchiveSerializer

logger = logging.getLogger(__name__)

new_cases_views = Blueprint("new_cases_views", __name__)

URL = "https://api1.datelazi.ro/api/v2/data/"


def store_yesterdays_stats(today, historical_data):
    past_days = sorted([d for d in historical_data if d != today])
    if not past_days:
        logger.error("No data for past days!")
        return

    yesterday = past_days[-1]
    serializer = DLZArchiveSerializer(historical_data[yesterday])
    db_stats = database.get_stats(COLLECTION["archive"], Data=yesterday)
    if db_stats and serializer.data.items() <= db_stats.items():
        logger.info(f"No updates for archive.")
        return

    serializer.save()
    logger.info(f"Updated archive stats for {yesterday}")


def sync_archive():
    response = requests.get(URL)
    response.raise_for_status()

    data = response.json()
    historical_data = data["historicalData"]

    for day in historical_data:
        serializer = DLZArchiveSerializer(historical_data[day])
        db_stats = database.get_stats(COLLECTION["archive"], Data=day)
        if db_stats and serializer.data.items() <= db_stats.items():
            logger.info(f"No updates for {day}")
            continue

        serializer.save()
        logger.info(f"Updated archive stats for {day}")


def get_quick_stats():
    response = requests.get(URL)
    response.raise_for_status()

    data = response.json()
    today_stats = data["currentDayStats"]
    historical_data = data["historicalData"]

    store_yesterdays_stats(today_stats["parsedOnString"], historical_data)

    serializer = DLZSerializer(today_stats)
    db_stats = database.get_stats(slug=SLUG["romania"])
    if db_stats and serializer.data.items() <= db_stats.items():
        logger.info("No updates for today's stats")
        return

    serializer.save()
    logger.info("Updated current day stats.")

    quick_stats = {
        field: data["currentDayStats"][DLZSerializer.mapped_fields[field]]
        for field in DLZSerializer.deserialize_fields
    }
    if db_stats and quick_stats.items() <= db_stats.items():
        logger.info("No updates to quick stats")
        return

    deserialized = serializer.deserialize(serializer.data)
    actualizat_la = deserialized.pop("Actualizat la")
    diff = utils.parse_diff(deserialized, db_stats)
    diff["Actualizat la"] = actualizat_la
    return formatters.parse_global(title="🔴 Cazuri noi", stats=diff, items={})


def get_latest_news():
    stats = scrapers.latest_article(json=True)

    db_stats = database.get_stats(slug=SLUG["stiri-oficiale"])
    if db_stats and stats.items() <= db_stats.items():
        return

    database.set_stats(
        stats=stats,
        collection=COLLECTION["romania"],
        slug=SLUG["stiri-oficiale"],
    )

    items = {stats.pop("descriere"): [stats.pop("url")]}
    return scrapers.formatters.parse_global(
        title=f"🔵 {stats.pop('titlu')}", stats=stats, items=items, emoji="❗"
    )


@new_cases_views.route("/check-<what>/<token>/", methods=["POST"])
def check_new_cases(what, token):
    if not database.get_collection("oicd_auth").find_one({"bearer": token}):
        raise abort(403)

    if what not in FUNCS:
        raise abort(404)

    text = FUNCS[what]()
    if not text:
        return "No changes"

    bot = telegram.Bot(token=TOKEN)
    return bot.sendMessage(
        chat_id=os.environ["CHAT_ID"],
        text=text,
        disable_notification=True,
        parse_mode=telegram.ParseMode.MARKDOWN,
    ).to_json()


FUNCS = {
    "covid-new-cases": get_quick_stats,
    "stiri-oficiale": get_latest_news,
    "sync-archive": sync_archive,
}
