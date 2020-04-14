import os

import telegram
from telegram.error import Unauthorized


def chunks(lst, width):
    """Yield successive n-sized chunks from lst."""
    for i in range(width):
        yield [
            lst[i + j * width]
            for j in range(width)
            if i + j * width < len(lst)
        ]


def send_message(bot, text, chat_id=None):
    try:
        return bot.send_message(
            chat_id=chat_id or os.getenv("DEBUG_CHAT_ID"),
            text=text,
            disable_notification=True,
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).to_json()
    except telegram.error.BadRequest as err:
        return bot.send_message(
            chat_id=chat_id or os.getenv("DEBUG_CHAT_ID"),
            text=str(err),
            disable_notification=True,
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).to_json()
    except Unauthorized as e:
        return str(e)
