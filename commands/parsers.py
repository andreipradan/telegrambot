def parse_details(data):
    items = list(data.items())
    return '├ ' + '\n├ '.join(
        [f'{" ".join(key.split("_"))}: {value}' for key, value in items[:-1]]
    ) + f'\n└ {items[-1][0]}: {items[-1][1]}'


def parse_list_details(data, item_emoji='➡️'):
    return '\n'.join([f"{item_emoji} {title}\n{parse_details(stats)}"
                      for title, stats in data.items()])


def parse_global(stats, items, title='🦠 Romania', emoji='➡️', footer='', bar_length=26):
    return f"""
{title}
{parse_details(stats)}

{parse_list_details(items, item_emoji=emoji)}
{footer}
{'=' * bar_length}
"""
