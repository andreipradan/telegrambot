from copy import deepcopy

import telegram

from core import constants


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def parse_diff(data, old_version):
    if not old_version:
        return data
    new = deepcopy(data)
    for key in data:
        new_value, old_value = data[key], old_version.get(key)
        if old_value and new_value != old_value:
            diff = new_value - old_value if old_value else 0
            new[key] = f"{new_value} ({'+' if diff >= 0 else ''}{diff})"
    return new


def parse_name(user):
    first_name = user.first_name or ""
    last_name = f"{' ' if first_name else ''}{user.last_name or ''}"
    return f"{first_name}{last_name}" or user.username


def parse_sentiment(data):
    if isinstance(data, str):
        return data
    score = data["Overall score"]
    if score < 0:
        return "Why so negative?"
    elif score > 0:
        return "Nice to see you positive like that!"
    return "You nailed it! You don't see everyday a neutral attitude."


def send_message(bot, text, chat_id=None):
    try:
        return bot.send_message(
            chat_id=chat_id or constants.DEBUG_CHAT_ID,
            text=text,
            disable_notification=True,
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).to_json()
    except telegram.error.BadRequest as err:
        return bot.send_message(
            chat_id=chat_id or constants.DEBUG_CHAT_ID,
            text=str(err),
            disable_notification=True,
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).to_json()
