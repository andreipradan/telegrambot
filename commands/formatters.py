def get_verbose(string):
    return " ".join(string.split("_")).capitalize()


def parse_details(data):
    if isinstance(data, dict):
        items = list(data.items())
        if len(items) > 1:
            return (
                "├ "
                + "\n├ ".join(
                    [f"{get_verbose(k)}: {v}" for k, v in items[:-1]]
                )
                + f"\n└ {get_verbose(items[-1][0])}: {items[-1][1]}"
            )
        return f"└ {get_verbose(items[-1][0])}: {items[-1][1]}"
    elif isinstance(data, list):
        items = data
        if len(items) > 1:
            return (
                "├ "
                + "\n├ ".join([value for value in items[:-1]])
                + f"\n└ {items[-1]}"
            )
        return f"└ {items[-1]}"


def parse_list_details(data, item_emoji="➡️"):
    return "\n".join(
        [
            f"\n{item_emoji} {title}\n{parse_details(stats)}"
            for title, stats in data.items()
        ]
    )


def parse_global(stats, items, title="🦠 Romania", emoji="➡️", footer=""):
    return f"""
{title}
{parse_details(stats)}
{parse_list_details(items, item_emoji=emoji)}
{footer}
"""
