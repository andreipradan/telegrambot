from copy import deepcopy
from datetime import timedelta

from app.public import blueprint
from flask import render_template
from flask import request

from app.public.utils import CHANGES
from app.public.utils import parse_countries
from app.public.utils import parse_countries_for_comparison
from app.public.utils import parse_top_stats
from core import database
from core.constants import SLUG, COLLECTION
from core.utils import epoch_to_timezone
from serializers import DLZArchiveSerializer

DATE_FORMAT = "%Y-%m-%d"
ICONS = {
    "Procent barbati": "male",
    "Procent femei": "female",
    "Procent copii": "child",
}


@blueprint.route("/")
def route_default():
    today = database.get_stats(slug=SLUG["romania"])
    today_date_time = epoch_to_timezone(today["Actualizat la"])
    today = {
        key: today[key]
        for key in [
            "Confirmați",
            "Decedați",
            "Vindecați",
            "Procent barbati",
            "Procent femei",
            "Procent copii",
        ]
    }

    archive_today = deepcopy(today)
    archive_today["Data"] = today_date_time.strftime(DATE_FORMAT)

    archive = list(database.get_many(COLLECTION["archive"], "Data", how=1))
    yesterday = today_date_time - timedelta(days=1)
    yesterday = [
        x for x in archive if x["Data"] == yesterday.strftime(DATE_FORMAT)
    ]
    archive = [
        DLZArchiveSerializer.deserialize(
            x, fields=["Confirmați", "Vindecați", "Decedați", "Data"]
        )
        for x in archive
    ] + [archive_today]
    return render_template(
        "home.html",
        today_stats_last_updated=today_date_time.strftime("%d.%m.%Y %H:%M"),
        archive=archive,
        top_stats=[
            {
                "name": key,
                "value": value,
                "icon": ICONS.get(key, "user"),
                "change": (today[key] - yesterday[0][key])
                if yesterday
                else None,
            }
            for key, value in today.items()
        ],
    )


@blueprint.route("/compare/", methods=["GET"])
def compare():
    available_countries = [
        country["code"]
        for country in database.get_collection("countries").find(
            {"code": {"$ne": None}}
        )
    ]

    selected_countries = request.args.getlist("country")
    etag = database.get_stats("etags", location="johns_hopkins")
    stats = database.get_stats(COLLECTION["country"], country="World")
    return render_template(
        "compare.html",
        top_stats=[
            {
                "name": key,
                "value": value,
                "icon": ICONS.get(key, "user"),
                "change": stats.get(CHANGES.get(key)),
            }
            for key, value in parse_top_stats(stats).items()
        ],
        archive=parse_countries_for_comparison(selected_countries),
        data_countries=",".join(available_countries),
        search_default=",".join(selected_countries),
        today_stats_last_updated=etag["last_updated"].strftime(
            "%d.%m.%Y %H:%M"
        )
        if etag
        else None,
    )


@blueprint.route("/global")
def global_map():
    countries = list(database.get_many(COLLECTION["country"], "total_cases"))
    stats = [c for c in countries if c["country"].strip() == "World"][0]
    return render_template(
        "global.html",
        today_stats_last_updated=database.get_stats(
            COLLECTION["global"], slug=SLUG["global"]
        )["last_updated"].replace("Last updated: ", ""),
        top_stats=[
            {
                "name": key,
                "value": value,
                "icon": ICONS.get(key, "user"),
                "change": stats.get(CHANGES.get(key)),
            }
            for key, value in parse_top_stats(stats).items()
        ],
        countries=parse_countries(countries),
    )


@blueprint.route("/europe")
def europe():
    countries = list(database.get_many(COLLECTION["country"], "total_cases"))
    europe_stats = [c for c in countries if c["country"].strip() == "Europe"][
        0
    ]
    return render_template(
        "europe.html",
        today_stats_last_updated=database.get_stats(
            COLLECTION["global"], slug=SLUG["global"]
        )["last_updated"].replace("Last updated: ", ""),
        top_stats=[
            {
                "name": key,
                "value": value,
                "icon": ICONS.get(key, "user"),
                "change": europe_stats.get(CHANGES.get(key)),
            }
            for key, value in parse_top_stats(europe_stats).items()
        ],
        countries=parse_countries(countries),
    )
