import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask import Flask
from flask import url_for

from core.views.base import make_json_response
from core.views.commands import commands_views
from core.views.new_cases import new_cases_views
from core.views.webhook import webhook_views

if not os.getenv("FLASK_DEBUG", False):
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"], integrations=[FlaskIntegration()]
    )

app = Flask(__name__)
app.register_blueprint(commands_views)
app.register_blueprint(new_cases_views)
app.register_blueprint(webhook_views)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/")
def site_map():
    links = [
        url_for(rule.endpoint, **(rule.defaults or {}), _external=True)
        for rule in app.url_map.iter_rules()
        if "GET" in rule.methods and has_no_empty_params(rule)
    ]
    return make_json_response(links)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=os.getenv("DEBUG", True),
    )
