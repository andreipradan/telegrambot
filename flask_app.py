import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask import Flask

from core.views.command import command_views
from core.views.country import country_views
from core.views.token import token_views

if not os.getenv('FLASK_DEBUG', False):
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[FlaskIntegration()]
    )

app = Flask(__name__)
app.register_blueprint(command_views)
app.register_blueprint(country_views)
app.register_blueprint(token_views)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8080)),
        debug=os.getenv('DEBUG', False),
    )
