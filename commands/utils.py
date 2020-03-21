def get_records_from_db(collection):
    return collection.find().sort({'TotalCases': -1})


def parse_country(data):
    items = list(data.items())
    return '\n├ '.join(
        [f'{key}: {value}' for key, value in items[1:-1]]
    ) + f'\n└{items[-1][0]}: {items[-1][1]}'


def parse_countries(countries):
    return '\n'.join(
        [
            f"""
🦠 {country}
├{parse_country(stats)}
""" for country, stats in countries.items()
        ]
    )


def parse_global(top_stats, countries, from_db=False):
    last_updated = top_stats.pop('last_updated')
    return f"""
Covid Global Stats
├{parse_country(top_stats)}
{parse_countries(countries)}

({last_updated}) [Source: {'DB' if from_db else 'worldometers.info/'}]
"""
