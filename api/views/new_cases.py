import logging
import os

import telegram
from flask import Blueprint
from flask import abort

from core import database
from core.auth import header_auth
from core.parsers import parse_diff
from core.utils import send_message
from core.utils import split_in_chunks
from scrapers.clients.datelazi import DateLaZiClient
from scrapers.clients.stirioficiale import StiriOficialeClient
from scrapers.formatters import parse_global
from serializers import DLZSerializer

logger = logging.getLogger(__name__)

new_cases_views = Blueprint("new_cases_views", __name__)


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

    quick_stats = DLZSerializer.deserialize(client.serialized_data)
    last_updated = quick_stats.pop("Actualizat la")

    db_stats = client._local_data
    if db_stats and quick_stats.items() <= db_stats.items():
        msg = "No updates to quick stats"
        logger.info(msg)
        return msg

    diff = parse_diff(quick_stats, db_stats)
    diff["Actualizat la"] = last_updated

    incidence = client.serialized_data["Incidență"]
    infections = client.serialized_data["Judete"]
    items = {
        "*Incidențe*": split_in_chunks(incidence, limit=5),
        "*Infectări*": split_in_chunks(infections, limit=5),
    }
    send_message(
        bot=telegram.Bot(token=os.environ["TOKEN"]),
        text=parse_global(
            title="🔴 Cazuri noi",
            stats=diff,
            items=items,
            footer="Detalii: https://telegrambot.pradan.dev/",
            emoji="🔸",
        ),
        chat_id=os.environ["CHAT_ID"],
    )
    msg = "Quick stats updated"
    logger.info(msg)
    return msg
