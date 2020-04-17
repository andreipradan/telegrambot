import os

import telegram

from flask import Blueprint
from flask import request

from core import inline
from core import handlers
from core import local_data
from core import utils
from core.constants import GOOGLE_CLOUD_COMMANDS
from core.constants import GOOGLE_CLOUD_WHITELIST
from powers.analyze_sentiment import analyze_sentiment
from powers.translate import translate_text

webhook_views = Blueprint("webhook_views", __name__)

TOKEN = os.environ["TOKEN"]


@webhook_views.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    json = request.get_json()
    if not json:
        raise ValueError("No payload")

    bot = telegram.Bot(token=TOKEN)
    update = telegram.Update.de_json(json, bot)

    command_text, status_code = handlers.validate_components(update)

    if command_text == "inline":
        if status_code in ["more", "back", "end"]:
            return getattr(inline, status_code)(update)
        return inline.refresh_data(update, getattr(local_data, status_code)())

    if status_code == 1337:
        if command_text == "skip-debug":
            return "ok"
        text = f"{command_text}.\nUpdate: {update.to_dict()}"
        return utils.send_message(bot, text=text)

    chat_id = update.message.chat.id
    if status_code != "valid-command":
        return utils.send_message(bot, text=command_text, chat_id=chat_id)

    if command_text == "start":
        return inline.start(update)

    if command_text in GOOGLE_CLOUD_COMMANDS:
        chat_type = update.message.chat.type
        if str(chat_id) not in GOOGLE_CLOUD_WHITELIST[chat_type]:
            return utils.send_message(bot, "Unauthorized", chat_id)

        arg = " ".join(update.message.text.split(" ")[1:])
        if command_text == "translate":
            return utils.send_message(bot, translate_text(arg), chat_id)
        if command_text == "analyze_sentiment":
            return utils.send_message(bot, analyze_sentiment(arg), chat_id)

    raise ValueError(f"Unhandled command: {command_text}, {status_code}")
