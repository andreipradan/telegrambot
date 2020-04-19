from copy import deepcopy

from app.public import blueprint
from flask import render_template

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
