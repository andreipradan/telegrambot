import os

import telegram
from flask import Blueprint
from flask import abort

from commands import histogram
from commands.parsers import parse_global
from core import constants
from core import database
from core.utils import parse_diff

new_cases_views = Blueprint('new_cases_views', __name__)


@new_cases_views.route('/check-covid-new-cases/<token>/', methods=['POST'])
def check_new_cases(token):
    if not database.get_collection('oicd_auth').find_one({'bearer': token}):
        raise abort(403)

    stats = histogram(json=True)
    stats = stats['quickStats']['totals']

    db_stats = database.get_stats(
        constants.COLLECTION['romania'],
        slug=constants.SLUG['romania']
    )
    if db_stats:
        db_stats.pop('_id')
        db_stats.pop('slug')
        if stats == db_stats:
            return 'No changes'

    database.set_stats(stats)

    text = parse_global(
        stats=parse_diff(stats, db_stats),
        items={},
    )
    bot = telegram.Bot(token=os.environ['TOKEN'])

    return bot.sendMessage(
        chat_id=412945234,
        text=text
    ).to_json()
