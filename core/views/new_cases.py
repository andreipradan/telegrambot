import os

import telegram
from flask import Blueprint
from flask import abort

from commands.parsers import parse_global
from core.constants import URLS
from commands.utils import request_total
from core import database
from core.utils import check_etag

new_cases_views = Blueprint('new_cases_views', __name__)


@new_cases_views.route('/check-covid-new-cases/<token>/', methods=['POST'])
def check_new_cases(token):
    if not database.get_collection('oicd_auth').find_one({'bearer': token}):
        raise abort(403)

    url = URLS['romania']
    if check_etag(url):
        return 'No changes'

    stats = request_total(url)
    text = parse_global(
        stats=stats,
        items={},
    )
    bot = telegram.Bot(token=os.environ['TOKEN'])

    return bot.sendMessage(
        chat_id=412945234,
        text=text
    ).to_json()
