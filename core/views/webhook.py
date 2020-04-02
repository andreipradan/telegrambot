import telegram

from flask import Blueprint
from flask import request

import scrapers
from core import inline
from core import constants
from core import handlers
from core import local_data
from core import utils
from powers.translate import translate_text

webhook_views = Blueprint("webhook_views", __name__)


@webhook_views.route(f"/{constants.TOKEN}", methods=["POST"])
def webhook():
    json = request.get_json()
    if not json:
        raise ValueError("No payload")

    bot = telegram.Bot(token=constants.TOKEN)
    update = telegram.Update.de_json(json, bot)

    if update.callback_query:
        data = update.callback_query.data
        if data == "end":
            return inline.end(update)
        elif data == "more":
            return inline.more(update)
        elif data == "back":
            return inline.back(update)
        return inline.refresh_data(update, getattr(local_data, data)())

    command_text, status_code = handlers.validate_components(update)

    if status_code == 1337:
        if command_text == "skip-debug":
            return "ok"
        text = f"{command_text}.\nUpdate: {update.to_dict()}"
        return utils.send_message(bot, text=text)

    chat_id = update.message.chat.id
    if status_code == "reply_to_message":
        return utils.send_message(
            bot,
            text=utils.parse_sentiment(
                scrapers.analyze_sentiment(command_text, json=True)
            ),
            chat_id=chat_id,
        )

    if status_code != "valid-command":
        return utils.send_message(bot, text=command_text, chat_id=chat_id)

    args = []
    if command_text in constants.COMMANDS_WITH_TEXT:
        args.append(" ".join(update.message.text.split(" ")[1:]))
    elif command_text in constants.COMMANDS_WITH_UPDATE:
        args.append(update)

    if command_text == "start":
        return inline.start(update)
    if command_text == "translate":
        if not all(args):
            return utils.send_message(bot, "You must provide the text", chat_id)
        return utils.send_message(bot, translate_text(" ".join(args)), chat_id)
    results = getattr(scrapers, command_text)(*args)

    try:
        utils.send_message(bot, text=results, chat_id=chat_id)
    except telegram.error.BadRequest as err:
        text = (
            f"Restrict results (e.g. /{command_text} 3"
            if "Message is too long" in str(err)
            else str(err)
        )
        utils.send_message(bot, text=text, chat_id=chat_id)
    return "completed"
