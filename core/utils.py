from datetime import datetime
import pytz
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


def epoch_to_timezone(epoch):
    utc_dt = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    tz = pytz.timezone("Europe/Bucharest")
    dt = utc_dt.astimezone(tz)
    return dt


def send_message(bot, text, chat_id=None):
    try:
        return bot.send_message(
            chat_id=chat_id or os.getenv("DEBUG_CHAT_ID"),
            text=text,
            disable_notification=True,
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).to_json()
    except telegram.error.BadRequest as err:
        try:
            return bot.send_message(
                chat_id=chat_id or os.getenv("DEBUG_CHAT_ID"),
                text=str(err),
                disable_notification=True,
                parse_mode=telegram.ParseMode.MARKDOWN,
            ).to_json()
        except Unauthorized as e:
            return str(e)
    except Unauthorized as e:
        return str(e)
