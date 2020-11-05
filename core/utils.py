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
    text = text.replace("_", "\\_")
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


def split_in_chunks(dct, chunk_size=15, limit=None):
    if not isinstance(dct, dict):
        raise ValueError("Must be instance of dict")
    if not dct:
        return
    if limit and limit < chunk_size:
        chunk_size = limit
    if len(dct) < chunk_size:
        chunk_size = len(dct)
    keys = list(reversed(sorted(dct, key=dct.get)))[:limit]
    max_key_len = len(keys[0])
    max_val_len = len(str(dct[keys[0]]))
    return [
        "  ".join(
            [
                f"`{name:<{max_key_len}}: {dct[name]:<{max_val_len}}`"
                for name in chunk
            ]
        )
        for chunk in chunks(keys, chunk_size)
    ]
