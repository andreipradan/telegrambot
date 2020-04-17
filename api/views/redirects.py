from flask import Blueprint
from flask import redirect

redirects_views = Blueprint("redirects_views", __name__)


@redirects_views.route("/bot")
def home():
    return redirect("https://telegram.me/alfred_the_robot")


@redirects_views.route("/channel/")
def channel():
    return redirect("https://t.me/covid_ro_updates")
