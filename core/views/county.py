from flask import Blueprint
from flask import abort
from flask import redirect
from flask import request
from flask import url_for

from core.constants import COLLECTION
from core.database import get_collection
from core.views.base import make_json_response

county_views = Blueprint('county_views', __name__)
home_view_name = 'county_views.counties'


def parse_item(result):
    result['_id'] = str(result['_id'])
    result['location'] = url_for(
        'county_views.county',
        slug=result['slug'],
        _external=True
    )
    return result


@county_views.route('/counties/')
def counties():
    url_params = request.args.to_dict()

    drop = url_params.get('drop')
    if drop:
        get_collection(COLLECTION[drop]).drop()
        return redirect('/counties/')

    skip = url_params.pop('start', 0)
    limit = url_params.pop('limit', 45)

    results = get_collection(COLLECTION['counties']).find(
        url_params
    ).sort(
        'Cazuri_confirmate', -1
    ).skip(skip).limit(limit)
    results = list(map(parse_item, results))
    return make_json_response(data=results)


@county_views.route('/counties/<slug>/')
def county(slug):
    result = get_collection(COLLECTION['counties']).find_one({'slug': slug})
    if result:
        return make_json_response(home=home_view_name, data=parse_item(result))
    return abort(404)
