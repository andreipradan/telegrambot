import os
from os import path
from importlib import import_module
from logging import DEBUG
from logging import StreamHandler
from logging import basicConfig
from logging import getLogger


from flask import Flask
from flask import url_for
from flask_login import LoginManager
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from api.views.new_cases import new_cases_views
from api.views.redirects import redirects_views
from api.views.webhook import webhook_views

login_manager = LoginManager()


def register_blueprints(app_instance):
    app_instance.register_blueprint(new_cases_views)
    app_instance.register_blueprint(redirects_views)
    app_instance.register_blueprint(webhook_views)

    for module_name in (
        "base",
        "forms",
        "ui",
        "home",
        "tables",
        "data",
        "additional",
        "base",
    ):
        module = import_module("app.{}.routes".format(module_name))
        app_instance.register_blueprint(module.blueprint)


def configure_logs():
    basicConfig(filename="error.log", level=DEBUG)
    logger = getLogger()
    logger.addHandler(StreamHandler())


def apply_themes(flask_app):
    """
    Add support for themes.

    If DEFAULT_THEME is set then all calls to
      url_for('static', filename='')
      will modfify the url to include the theme name

    The theme parameter can be set directly in url_for as well:
      ex. url_for('static', filename='', theme='')

    If the file cannot be found in the /static/<theme>/ location then
      the url will not be modified and the file is expected to be
      in the default /static/ location
    """

    @flask_app.context_processor
    def override_url_for():
        return dict(url_for=_generate_url_for_theme)

    def _generate_url_for_theme(endpoint, **values):
        if endpoint.endswith("static"):
            theme = values.get("theme", None) or flask_app.config.get(
                "DEFAULT_THEME", None
            )
            if theme:
                theme_file = "{}/{}".format(theme, values.get("filename", ""))
                if path.isfile(path.join(flask_app.static_folder, theme_file)):
                    values["filename"] = theme_file
            if flask_app.env != "development":
                return (
                    f"{os.getenv('STATIC_HOST')}{url_for(endpoint, **values)}"
                )
        return url_for(endpoint, **values)


def create_app():
    app = Flask(__name__, static_folder="app/base/static",)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    login_manager.init_app(app)
    register_blueprints(app)
    configure_logs()
    apply_themes(app)
    return app


SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"], integrations=[FlaskIntegration()]
    )

app = create_app()
if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 5000)),
        debug=os.getenv("DEBUG", False),
    )
