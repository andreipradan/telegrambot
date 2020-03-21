def get_records_from_db(collection):
    return collection.find().sort({'TotalCases': -1})


def parse_country(data):
    return '\n\t'.join([f'{key}: {value}' for key, value in data.items()])
