import pycountry

from core import database


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


def get_day_from_history(date, history):
    for d in history:
        if d["date"].strftime("%Y-%m-%d") == date:
            return d


def parse_countries_for_comparison(countries):
    if not countries:
        return []

    first_country = database.get_stats("countries", country=countries[0])
    if not first_country:
        return []
    results = [
        {
            "date": day["date"].strftime("%Y-%m-%d"),
            countries[0]: day["confirmed"],
        }
        for day in first_country["history"]
    ]

    for country in countries[1:]:
        country = database.get_stats("countries", country=country)
        if not country:
            continue
        for i in results:
            history = country["history"] if country else []
            i[country["country"]] = get_day_from_history(i["date"], history)[
                "confirmed"
            ]
    return [
        country
        for country in results
        if any([int(val) for key, val in country.items() if key != "date"])
    ]