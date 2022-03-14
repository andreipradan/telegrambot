import logging
import os

import telegram
from flask import Blueprint

from core.auth import header_auth
from core.parsers import parse_diff
from core.utils import send_message
from core.utils import split_in_chunks
from scrapers.clients.datelazi import DateLaZiClient
from scrapers.formatters import parse_global
from serializers import DLZSerializer

logger = logging.getLogger(__name__)

new_cases_views = Blueprint("new_cases_views", __name__)


@new_cases_views.route("/sync-archive/", methods=["POST"])
@header_auth
def sync_archive():
    text = DateLaZiClient().sync_archive()
    if not text:
        return "No changes"

    bot = telegram.Bot(token=os.environ["TOKEN"])
    return bot.sendMessage(
        chat_id=os.environ["CHAT_ID"],
        text=text,
        disable_notification=True,
        parse_mode=telegram.ParseMode.MARKDOWN,
    ).to_json()


@new_cases_views.route("/check-new-cases/", methods=["POST"])
@header_auth
def check_quick_stats():
    client = DateLaZiClient()
    client.sync()

    quick_stats = DLZSerializer.deserialize(client.serialized_data)
    last_updated = quick_stats.pop("Data")

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
        "*Vaccinări*": [
            f"`Total: {client.serialized_data['Total doze administrate']}`",
        ],
        **{
            f"*{company.title()} (24h)*": {
                "Total": f'+{data["total_administered"]}',
                "Rapel": f'+{data["immunized"]}',
            }
            for company, data in client.serialized_data.get(
                "Vaccinări", {}
            ).items()
            if data["total_administered"] or data["immunized"]
        },
    }
    send_message(
        bot=telegram.Bot(token=os.environ["TOKEN"]),
        text=parse_global(
            title="🔴 Cazuri noi",
            stats=diff,
            items=items,
            footer="\nDetalii: https://coronavirus.pradan.dev/",
            emoji="🔸",
        ),
        chat_id=os.environ["CHAT_ID"],
    )
    msg = "Quick stats updated"
    logger.info(msg)
    return msg
