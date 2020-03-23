import os

import requests
import telegram
from flask import Blueprint
from flask import abort

from commands import utils
from commands.parsers import parse_global
from core.constants import URLS
from commands.utils import request_romania, check_etag
from core import database

new_cases_views = Blueprint('new_cases_views', __name__)


@new_cases_views.route('/check-covid-new-cases/<token>/', methods=['POST'])
def check_new_cases(token):
    if not database.get_collection('oicd_auth').find_one({'bearer': token}):
        raise abort(403)

    if check_etag(URLS['ROMANIA']):
        return 'No changes'

    stats = request_romania()
    last_updated = utils.get_date(stats.pop('EditDate'))
    text = parse_global(
        stats=stats,
        items={},
        footer=f'Last updated: {last_updated}\n[Source API]'
    )
    bot = telegram.Bot(token=os.environ['TOKEN'])

    return bot.sendMessage(
        chat_id=412945234,
        text=text
    ).to_json()