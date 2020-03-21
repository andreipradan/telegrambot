import os

import requests
import telegram
from flask import Blueprint
from flask import abort

from core.constants import ROMANIA_STATS_SLUG
from core.constants import URLS
from commands.covid_stats import request_romania
from core import database

covid_views = Blueprint('covid_views', __name__)


@covid_views.route('/check-covid-new-cases/<token>/', methods=['POST'])
def check_new_cases(token):
    if not database.get_collection('oicd_auth').find_one({'bearer': token}):
        raise abort(403)

    url = URLS['ROMANIA']
    head = requests.head(url)
    head.raise_for_status()

    db_stats = database.get_stats_by_slug(ROMANIA_STATS_SLUG)

    head_etag = head.headers.get('ETag')
    db_etag = db_stats.get('ETag')
    if head_etag and db_etag and head_etag == db_etag:
        return 'No changes'

    bot = telegram.Bot(token=os.environ['TOKEN'])
    return bot.sendMessage(
        chat_id=412945234,
        text=request_romania()
    ).to_json()
