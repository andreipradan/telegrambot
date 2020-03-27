import os

import telegram
from flask import Blueprint
from flask import abort

import commands
from commands import parsers
from core import constants
from core import database
from core import utils

new_cases_views = Blueprint('new_cases_views', __name__)


def get_histogram():
    stats = commands.histogram(json=True)['quickStats']['totals']
    db_stats = database.get_stats(
        constants.COLLECTION['romania'],
        slug=constants.SLUG['romania']
    )
    if db_stats:
        db_stats.pop('_id')
        db_stats.pop('slug')
        if stats.items() <= db_stats.items():
            return

    database.set_stats(stats)

    return parsers.parse_global(
        title='🔴 Cazuri noi',
        stats=utils.parse_diff(stats, db_stats),
        items={},
    )


def get_latest_news():
    stats = commands.latest_article(json=True)

    db_stats = database.get_stats(
        constants.COLLECTION['romania'],
        slug=constants.SLUG['stiri-oficiale']
    )
    if db_stats:
        db_stats.pop('_id')
        db_stats.pop('slug')
        if stats.items() <= db_stats.items():
            return

    database.set_stats(stats, slug=constants.SLUG['stiri-oficiale'])

    items = {stats.pop('description'): [stats.pop('url')]}
    return parsers.parse_global(
        title=f"🔵 {stats.pop('title')}",
        stats=stats,
        items=items,
        emoji='❗'
    )


@new_cases_views.route('/check-<what>/<token>/', methods=['POST'])
def check_new_cases(what, token):
    if not database.get_collection('oicd_auth').find_one({'bearer': token}):
        raise abort(403)

    if what not in FUNCS:
        raise abort(404)

    bot = telegram.Bot(token=os.environ['TOKEN'])

    text = FUNCS[what]()
    if not text:
        return 'No changes'

    return bot.sendMessage(
        chat_id=constants.IDS['covid-updates'],
        text=text,
        disable_notification=True,
    ).to_json()


FUNCS = {
    'covid-new-cases': get_histogram,
    'stiri-oficiale': get_latest_news,
}
