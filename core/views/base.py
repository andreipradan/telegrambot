from functools import wraps

from flask import g
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)
    return decorated_function


def make_json_response(data=None, errors=None, links=None, home='site_map'):
    links = links or {}
    links.update({'home': url_for(home, _external=True)})
    return jsonify(
        {
            'count': len(data) if data else 0,
            'data': data or {},
            'errors': errors or [],
            'links': links,
        }
    ), 200 if not errors else 400
