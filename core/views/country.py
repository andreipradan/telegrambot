from flask import Blueprint
from flask import abort
from flask import redirect
from flask import request

from core.database import get_collection
from core.database import update_or_create
from core.handlers import parse_result
from core.views.base import make_json_response

country_views = Blueprint('country_views', __name__)
home_view_name = 'country_views.country_list'


@country_views.route('/countries/')
def country_list():
    url_params = request.args.to_dict()
    limit = url_params.get('limit', 10)
    results = list(map(parse_result, get_collection().find().sort(
        'TotalCases', -1
    )[:limit]))
    return make_json_response(home_view_name=home_view_name, data=results)


@country_views.route('/countries/add/')
def country_add():
    if not request.args:
        return 'Invalid data. Retry using URL parameters'
    update_or_create(**request.args.to_dict())
    return redirect('/collections')


@country_views.route('/countries/<slug>/')
def country_details(slug):
    result = get_collection().find_one({'slug': slug})
    if result:
        return make_json_response(home_view_name, parse_result(result))
    return abort(404)
