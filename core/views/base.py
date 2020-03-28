from flask import jsonify
from flask import url_for


def get_count(data):
    return len(data) if isinstance(data, list) else 1 if data else 0


def make_json_response(data=None, errors=None, links=None, home="site_map"):
    links = links or {}
    links.update({"home": url_for(home, _external=True)})
    return (
        jsonify(
            {
                "count": get_count(data),
                "data": data or {},
                "errors": errors or [],
                "links": links,
            }
        ),
        200 if not errors else 400,
    )
