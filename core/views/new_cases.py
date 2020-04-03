import requests
import telegram
from flask import Blueprint
from flask import abort

import scrapers
from scrapers import formatters
from core import constants
from core import database
from core import utils
from serializers import DLZSerializer

new_cases_views = Blueprint("new_cases_views", __name__)

URL = "https://api1.datelazi.ro/api/v2/data/"


def get_quick_stats():
    response = requests.get(URL)
    response.raise_for_status()
    stats = DLZSerializer.serialize(response.json()["currentDayStats"])

    db_stats = database.get_stats()
    if db_stats and stats.items() <= db_stats.items():
        return

    database.set_stats(stats)

    return formatters.parse_global(
        title="🔴 Cazuri noi",
        stats=utils.parse_diff(stats, db_stats),
        items={},
    )


def get_latest_news():
    stats = scrapers.latest_article(json=True)

    db_stats = database.get_stats(slug=constants.SLUG["stiri-oficiale"])
    if db_stats and stats.items() <= db_stats.items():
        return

    database.set_stats(stats, slug=constants.SLUG["stiri-oficiale"])

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

    bot = telegram.Bot(token=constants.TOKEN)
    return bot.sendMessage(
        chat_id=constants.CHAT_ID, text=text, disable_notification=True,
    ).to_json()


FUNCS = {
    "covid-new-cases": get_quick_stats,
    "stiri-oficiale": get_latest_news,
}
