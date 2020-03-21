def get_records_from_db(collection):
    return collection.find().sort({'TotalCases': -1})


def parse_details(data):
    items = list(data.items())
    return f'├ ' + '\n├ '.join(
        [f'{key}: {value}' for key, value in items[:-1]]
    ) + f'\n└ {items[-1][0]}: {items[-1][1]}'


def parse_list_details(data, item_emoji='➡️'):
    return '\n'.join([f"{item_emoji} {title}\n{parse_details(stats)}"
                      for title, stats in data.items()])


def parse_global(title, top_stats, items, item_emoji='➡️', footer=''):
    return f"""
{title}
{parse_details(top_stats)}

{parse_list_details(items, item_emoji=item_emoji)}

{footer}
"""
