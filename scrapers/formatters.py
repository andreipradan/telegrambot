def field_to_string(string):
    return " ".join(string.split("_")).capitalize()


def string_to_field(field):
    return "_".join([part.lower() for part in field.split(" ")])


def parse_details(data):
    if not data:
        raise ValueError("data must not be null, empty, etc.")

    if isinstance(data, dict):
        items = list(data.items())
        if len(items) > 1:
            return (
                "├ "
                + "\n├ ".join(
                    [f"{field_to_string(k)}: {v}" for k, v in items[:-1]]
                )
                + f"\n└ {field_to_string(items[-1][0])}: {items[-1][1]}"
            )
        return f"└ {field_to_string(items[-1][0])}: {items[-1][1]}"
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
