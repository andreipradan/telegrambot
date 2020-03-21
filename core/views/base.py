from flask import jsonify
from flask import url_for


def make_json_response(home_view_name, data=None, errors=None):
    return jsonify(
        {
            'count': len(data) if data else 0,
            'data': data or {},
            'errors': errors,
            'links': {
                'home': url_for(home_view_name, _external=True),
            }
        }
    ), 200 if not errors else 400
