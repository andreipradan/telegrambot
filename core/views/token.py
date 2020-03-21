import os

import telegram

from flask import Blueprint
from flask import request

from core.handlers import ALLOWED_COMMANDS
from core.handlers import COMMANDS_WITH_TEXT
from core.handlers import COMMANDS_WITH_UPDATE
from core.handlers import validate_components

token_views = Blueprint('token_views', __name__)


def send_message(bot, text, chat_id=None):
    return bot.sendMessage(
        chat_id=chat_id or 412945234,
        text=text
    ).to_json()


@token_views.route(f"/{os.environ['TOKEN']}", methods=['POST'])
def telegram_webhook():
    if request.method == "POST":
        json = request.get_json()
        if not json:
            raise ValueError('No payload')

        bot = telegram.Bot(token=os.environ['TOKEN'])
        update = telegram.Update.de_json(json, bot)

        command_text, error_code = validate_components(update.message)

        chat_id = update.message.chat_id

        if error_code == 404:
            raise ValueError(f'{command_text}. Update: {update.to_dict()}')
        elif error_code == 400:
            return send_message(bot, text=command_text, chat_id=chat_id)
        elif error_code == 1337:
            return send_message(bot, command_text, chat_id=412945234)

        args = []
        if command_text in COMMANDS_WITH_TEXT:
            args.append(' '.join(update.message.text.split(' ')[1:]))
        elif command_text in COMMANDS_WITH_UPDATE:
            args.append(update)
        results = ALLOWED_COMMANDS[command_text](*args)

        try:
            bot.sendMessage(chat_id=chat_id, text=results)
        except telegram.error.BadRequest as err:
            text = (
                f'Restrict results (e.g. /{command_text} 3'
                if 'Message is too long' in str(err)
                else str(err)
            )
            bot.sendMessage(chat_id=chat_id, text=text)
        return 'completed'
    return f"Unexpected method {request.method}"
