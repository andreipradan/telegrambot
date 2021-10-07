import os
from copy import deepcopy
from datetime import timedelta, datetime

from app.public import blueprint
from flask import render_template
from flask import request

from app.public.utils import CHANGES
from app.public.utils import parse_countries
from app.public.utils import parse_countries_for_comparison
from app.public.utils import parse_top_stats
from core import database
from core.constants import SLUG, COLLECTION, DATE_FORMAT
from serializers import DLZArchiveSerializer

ICONS = {
    "Procent barbati": "male",
    "Procent femei": "female",
    "Procent copii": "child",
}


@blueprint.route("/")
def route_default():
    today = database.get_stats(slug=SLUG["romania"])
    if not today:
        return render_template(
            "home.html", archive=[], stats_last_updated="N/A"
        )
    incidence = today.get("Incidență", {})
    infections = today.get("Judete", {})
    today_date = datetime.strptime(today["Data"], DATE_FORMAT)

    today_keys = ["Confirmați", "Decedați", "Vindecați"]
    if not os.environ["DATELAZI_DATA_URL"].endswith("smallData.json"):
        today_keys.extend(
            ["Procent barbati", "Procent femei", "Procent copii"]
        )
    today = {key: today[key] for key in today_keys}

    archive_today = deepcopy(today)
    archive_today["Data"] = today_date

    archive = list(database.get_many(COLLECTION["archive"], "Data", how=1))
    yesterday = today_date - timedelta(days=1)
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
        stats_last_updated=today_date.strftime("%d.%m.%Y"),
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
        incidence=[
            {"county": c, "incidence": incidence[c]} for c in incidence.keys()
        ],
        infections=[
            {"county": c, "infections": infections[c]}
            for c in infections.keys()
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
    if not stats:
        return render_template(
            "compare.html", archive=[], stats_last_updated="N/A"
        )
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
        stats_last_updated=etag["last_updated"].strftime("%d.%m.%Y %H:%M")
        if etag
        else None,
    )


@blueprint.route("/global")
def global_map():
    countries = list(database.get_many(COLLECTION["country"], "total_cases"))
    if not countries:
        return render_template(
            "global.html", countries=[], stats_last_updated="N/A"
        )
    stats = [c for c in countries if c["country"].strip() == "World"][0]
    return render_template(
        "global.html",
        stats_last_updated=database.get_stats(
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
    if not countries:
        return render_template(
            "europe.html", countries=[], stats_last_updated="N/A"
        )
    europe_stats = [c for c in countries if c["country"].strip() == "Europe"][
        0
    ]
    return render_template(
        "europe.html",
        stats_last_updated=database.get_stats(
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
