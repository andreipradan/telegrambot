import logging
import os

import requests
import telegram
from flask import Blueprint
from flask import abort

from core import database
from core.auth import header_auth
from core.constants import COLLECTION
from core.constants import SLUG
from core.parsers import parse_diff
from core.utils import send_message
from core.validators import is_valid_date
from scrapers.clients.datelazi import DateLaZiClient
from scrapers.clients.stirioficiale import StiriOficialeClient
from scrapers.formatters import parse_global
from serializers import DLZSerializer
from serializers import DLZArchiveSerializer

logger = logging.getLogger(__name__)

new_cases_views = Blueprint("new_cases_views", __name__)


def store_yesterdays_stats(today, historical_data):
    past_days = sorted(
        [d for d in historical_data if d != today and is_valid_date(d)]
    )
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


def get_latest_news():
    client = StiriOficialeClient()
    stats = client.sync()
    if not stats:
        return

    items = {stats.pop("descriere"): [stats.pop("url")]}
    return parse_global(
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

    bot = telegram.Bot(token=os.environ["TOKEN"])
    return bot.sendMessage(
        chat_id=os.environ["CHAT_ID"],
        text=text,
        disable_notification=True,
        parse_mode=telegram.ParseMode.MARKDOWN,
    ).to_json()


FUNCS = {
    "stiri-oficiale": get_latest_news,
    "sync-archive": DateLaZiClient().sync_archive,
}


@new_cases_views.route("/check-new-cases/", methods=["POST"])
@header_auth
def check_quick_stats():
    client = DateLaZiClient()
    client.sync()

    # TODO: add sync_archive (or separate endpoint to check less often
    #  e.g. only once a day)

    quick_stats = DLZSerializer.deserialize(client.serialized_data)
    last_updated = quick_stats.pop("Actualizat la")

    db_stats = client._local_data
    if db_stats and quick_stats.items() <= db_stats.items():
        msg = "No updates to quick stats"
        logger.info(msg)
        return msg

    diff = parse_diff(quick_stats, db_stats)
    diff["Actualizat la"] = last_updated

    send_message(
        bot=telegram.Bot(token=os.environ["TOKEN"]),
        text=parse_global(title="🔴 Cazuri noi", stats=diff, items={}),
        chat_id=os.environ["CHAT_ID"],
    )
    msg = "Quick stats updated"
    logger.info(msg)
    return msg
