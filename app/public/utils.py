import pycountry
from flask import flash

from core import database

CHANGES = {"Confirmați": "new_cases", "Decedați": "new_deaths"}


def parse_countries(countries):
    results = {}
    invalid = []
    c_map = {c.name: c.alpha_2 for c in pycountry.countries}

    for country in countries:
        country_name = country["country"].strip()
        if not country_name:
            continue
        if country_name in [
            "World",
            "Europe",
            "North America",
            "Asia",
            "South America",
            "Africa",
            "Oceania",
            "Diamond Princess",
            "MS Zaandam",
            "Caribbean Netherlands",
            "Channel Islands",
        ]:
            continue
        if country_name == "USA":
            country_name = "United States"
        if country_name == "UK":
            country_name = "United Kingdom"
        if country_name == "Russia":
            country_name = "Russian Federation"
        if country_name == "S. Korea":
            country_name = "Korea, Republic of"
        if country_name == "Iran":
            country_name = "Iran, Islamic Republic of"
        if country_name == "UAE":
            country_name = "United Arab Emirates"
        if country_name == "Moldova":
            country_name = "Moldova, Republic of"
        if country_name == "Ivory Coast":
            country_name = "Côte d'Ivoire"
        if country_name == "Palestine":
            country_name = "Palestine, State of"
        if country_name == "Taiwan":
            country_name = "Taiwan, Province of China"
        if country_name == "Laos":
            country_name = "Lao People's Democratic Republic"
        if country_name == "St. Barth":
            country_name = "Saint Barthélemy"
        if country_name == "Vatican City":
            country_name = "Holy See (Vatican City State)"
        if country_name == "Tanzania":
            country_name = "Tanzania, United Republic of"
        if country_name == "Vietnam":
            country_name = "Viet Nam"
        if country_name == "Bolivia":
            country_name = "Bolivia, Plurinational State of"
        if country_name == "Venezuela":
            country_name = "Venezuela, Bolivarian Republic of"
        if country_name == "Faeroe Islands":
            country_name = "Faroe Islands"
        if country_name == "Brunei":
            country_name = "Brunei Darussalam"
        if country_name == "Syria":
            country_name = "Syrian Arab Republic"
        if country_name == "DRC":
            country_name = "Congo, The Democratic Republic of the"
        if country_name == "Saint Martin":
            country_name = "Saint Martin (French part)"
        if country_name == "CAR":
            country_name = "Central African Republic"
        if country_name == "St. Vincent Grenadines":
            country_name = "Saint Vincent and the Grenadines"
        if country_name == "Turks and Caicos":
            country_name = "Turks and Caicos Islands"
        if country_name == "Falkland Islands":
            country_name = "Falkland Islands (Malvinas)"
        if country_name == "Sint Maarten":
            country_name = "Sint Maarten (Dutch part)"
        if country_name == "Saint Pierre Miquelon":
            country_name = "Saint Pierre and Miquelon"
        if country_name == "British Virgin Islands":
            country_name = "Virgin Islands, British"

        country.pop("_id")
        try:
            code = c_map[country_name].lower()
        except KeyError:
            invalid.append(country_name)
            continue
        results[code] = country
    if invalid:
        raise ValueError(invalid)

    return results


def parse_countries_for_comparison(codes):
    """
    :param codes: country codes
    :return: [{"date": 2020-12-31, "Germany": 4, "Austria": 5}, {..}]
    """

    if not codes:
        return []

    codes = [code.lower() for code in codes]
    countries = database.get_collection("countries").find(
        {"code": {"$in": codes}}
    )

    results = {}
    no_info_countries = []
    for country in countries:
        for day in country["history"]:
            try:
                results.setdefault(day["date"], {})[country["country"]] = day[
                    "confirmed"
                ]
            except KeyError:
                if country["country"] not in no_info_countries:
                    no_info_countries.append(country["country"])
    if no_info_countries:
        flash(
            "Următoarele țări conțin date incomplete și nu au fost afișate: "
            f"{', '.join(no_info_countries)}"
        )
    return [
        {"date": k, **results[k]}
        for k in results
        if any([int(x) for _, x in results[k].items()])
    ]


def parse_top_stats(stats):
    return {
        "Confirmați": "{:,}".format(stats["total_cases"]),
        "Decedați": "{:,}".format(stats["total_deaths"]),
        "Vindecati": "{:,}".format(stats["total_recovered"]),
        "Cazuri critice": "{:,}".format(stats["serious_critical"]),
        "Cazuri active": "{:,}".format(stats["active_cases"]),
    }
