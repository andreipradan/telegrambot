from flask import Blueprint, url_for
from flask import abort
from flask import request

from core.constants import COLLECTION
from core.database import get_collection
from core.views.base import make_json_response

county_views = Blueprint('county_views', __name__)
home_view_name = 'county_views.country_list'


def parse_item(result):
    result['_id'] = str(result['_id'])
    result['location'] = url_for(
        'county_views.county',
        slug=result['slug'],
        _external=True
    )
    return result


@county_views.route('/counties/')
def county_list():
    url_params = request.args.to_dict()
    limit = url_params.pop('limit', 10)
    results = list(map(parse_item, get_collection(COLLECTION['counties']).find(
        url_params
    ).sort(
        'Cazuri_confirmate', -1
    )[:limit]))
    return make_json_response(data=results)


@county_views.route('/counties/<slug>/')
def county(slug):
    result = get_collection(COLLECTION['counties']).find_one({'slug': slug})
    if result:
        return make_json_response(home_view_name, parse_item(result))
    return abort(404)
