import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask import Flask
from flask import redirect

from core.views.new_cases import new_cases_views
from core.views.webhook import webhook_views

SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"], integrations=[FlaskIntegration()]
    )

app = Flask(__name__)
app.register_blueprint(new_cases_views)
app.register_blueprint(webhook_views)


@app.route("/")
def home():
    return redirect("https://telegram.me/alfred_the_robot")


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 5000)),
        debug=os.getenv("DEBUG", False),
    )
