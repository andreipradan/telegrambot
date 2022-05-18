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
        elif country_name in [
            "Africa",
            "Asia",
            "Caribbean Netherlands",
            "Channel Islands",
            "Diamond Princess",
            "Europe",
            "MS Zaandam",
            "North America",
            "Oceania",
            "South America",
            "Total",
            "Total:",
            "World",
        ]:
            continue
        elif country_name == "USA":
            country_name = "United States"
        elif country_name == "UK":
            country_name = "United Kingdom"
        elif country_name == "Russia":
            country_name = "Russian Federation"
        elif country_name == "S. Korea":
            country_name = "Korea, Republic of"
        elif country_name == "Iran":
            country_name = "Iran, Islamic Republic of"
        elif country_name == "UAE":
            country_name = "United Arab Emirates"
        elif country_name == "Moldova":
            country_name = "Moldova, Republic of"
        elif country_name == "Ivory Coast":
            country_name = "Côte d'Ivoire"
        elif country_name == "Palestine":
            country_name = "Palestine, State of"
        elif country_name == "Taiwan":
            country_name = "Taiwan, Province of China"
        elif country_name == "Laos":
            country_name = "Lao People's Democratic Republic"
        elif country_name == "St. Barth":
            country_name = "Saint Barthélemy"
        elif country_name == "Vatican City":
            country_name = "Holy See (Vatican City State)"
        elif country_name == "Tanzania":
            country_name = "Tanzania, United Republic of"
        elif country_name == "Vietnam":
            country_name = "Viet Nam"
        elif country_name == "Bolivia":
            country_name = "Bolivia, Plurinational State of"
        elif country_name == "Venezuela":
            country_name = "Venezuela, Bolivarian Republic of"
        elif country_name == "Faeroe Islands":
            country_name = "Faroe Islands"
        elif country_name == "Brunei":
            country_name = "Brunei Darussalam"
        elif country_name == "Syria":
            country_name = "Syrian Arab Republic"
        elif country_name == "DRC":
            country_name = "Congo, The Democratic Republic of the"
        elif country_name == "Saint Martin":
            country_name = "Saint Martin (French part)"
        elif country_name == "CAR":
            country_name = "Central African Republic"
        elif country_name == "St. Vincent Grenadines":
            country_name = "Saint Vincent and the Grenadines"
        elif country_name == "Turks and Caicos":
            country_name = "Turks and Caicos Islands"
        elif country_name == "Falkland Islands":
            country_name = "Falkland Islands (Malvinas)"
        elif country_name == "Sint Maarten":
            country_name = "Sint Maarten (Dutch part)"
        elif country_name == "Saint Pierre Miquelon":
            country_name = "Saint Pierre and Miquelon"
        elif country_name == "British Virgin Islands":
            country_name = "Virgin Islands, British"
        elif country_name == "Micronesia":
            country_name = "Micronesia, Federated States of"
        elif country_name == "Saint Helena":
            country_name = "Saint Helena, Ascension and Tristan da Cunha"
        elif country_name == "DPRK":
            country_name = "Korea, Democratic People's Republic of"

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
