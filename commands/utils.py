def get_records_from_db(collection):
    return collection.find().sort({'TotalCases': -1})


def parse_country(data):
    items = list(data.items())
    return '\n├ '.join(
        [f'{key}: {value}' for key, value in items[:-1]]
    ) + f'\n└{items[-1][0]}: {items[-1][1]}'


def parse_global_countries(countries):
    return '\n'.join(
        [
            f"""
    🦠 {country}:
    ├ {parse_country(stats)}""" for country, stats in countries.items()
        ]
    )


def parse_global(last_updated_string, cases, deaths, recovered, countries):
    return f"""
        Covid Global Stats ({last_updated_string})
    {cases[0]}  {cases[1]}
    {deaths[0]}                     {deaths[1]}
    {recovered[0]}              {recovered[1]}
    {parse_global_countries(countries)}
    """
