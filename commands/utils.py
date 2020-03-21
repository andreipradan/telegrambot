def get_records_from_db(collection):
    return collection.find().sort({'TotalCases': -1})


def parse_country(data):
    items = data.items()
    return '\n├ '.join(
        [f'{key}: {value}' for key, value in items[:-1]]
    ) + f'└{items[-1][0]}: {items[-1][1]}'
