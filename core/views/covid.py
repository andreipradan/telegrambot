from flask import Blueprint, request

from core.database import get_collection

covid_views = Blueprint('covid_views', __name__)


@covid_views.route('/check-covid-new-cases/', methods=['POST'])
def check_new_cases():
    oicd_collection = get_collection('oicd_auth')
    oicd_collection.insert_one({'bearer': request.headers.get('Authorization')})
    return 'ok'
