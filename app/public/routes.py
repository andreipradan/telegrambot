from copy import deepcopy


from app.public import blueprint
from flask import render_template
from flask import request

from app.public.utils import parse_countries
from app.public.utils import parse_countries_for_comparison
from core import database
from core.constants import SLUG, COLLECTION
from core.utils import epoch_to_timezone
from serializers import DLZArchiveSerializer

ICONS = {
    "Procent barbati": "male",
    "Procent femei": "female",
    "Procent copii": "child",
}


@blueprint.route("/")
def route_default():
    today = database.get_stats(slug=SLUG["romania"])
    today_date = epoch_to_timezone(today["Actualizat la"]).strftime("%Y-%m-%d")
    archive = list(
        database.get_many(
            collection=COLLECTION["archive"], order_by="Data", how=1
        )
    )

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
    archive_today["Data"] = today_date
    return render_template(
        "home.html",
        archive=[DLZArchiveSerializer.deserialize(x) for x in archive]
        + [archive_today],
        top_stats=[
            {
                "name": key,
                "value": value,
                "icon": ICONS.get(key, "user"),
                "change": (today[key] - archive[-1][key]) if archive else None,
            }
            for key, value in today.items()
            if key != "Actualizat la"
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
    parsed = parse_countries_for_comparison(selected_countries)
    return render_template(
        "compare.html",
        archive=parsed,
        search_default=",".join(selected_countries),
        data_countries=",".join(available_countries),
    )


@blueprint.route("/global")
def global_map():
    stats = database.get_stats(COLLECTION["global"], slug=SLUG["global"])
    stats = {
        "Confirmați": stats["coronavirus_cases:"],
        "Decedați": stats["deaths:"],
        "Vindecați": stats["recovered:"],
    }
    countries = database.get_many(COLLECTION["country"], "total_cases")

    return render_template(
        "global.html",
        top_stats=[
            {"name": key, "value": value, "icon": ICONS.get(key, "user"),}
            for key, value in stats.items()
        ],
        countries=parse_countries(countries),
    )


@blueprint.route("/europe")
def europe():
    countries = list(database.get_many(COLLECTION["country"], "total_cases"))
    europe_stats = [c for c in countries if c["country"].strip() == "Europe"][
        0
    ]
    stats = {
        "Confirmați": "{:,}".format(europe_stats["total_cases"]),
        "Decedați": "{:,}".format(europe_stats["total_deaths"]),
        "Vindecati": "{:,}".format(europe_stats["total_recovered"]),
    }

    return render_template(
        "europe.html",
        top_stats=[
            {"name": key, "value": value, "icon": ICONS.get(key, "user"),}
            for key, value in stats.items()
        ],
        countries=parse_countries(countries),
    )
