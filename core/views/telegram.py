import os

import telegram

from flask import Blueprint
from flask import request

from core.handlers import ALLOWED_COMMANDS, COMMANDS_WITH_UPDATE_AND_BOT
from core.handlers import COMMANDS_WITH_TEXT
from core.handlers import COMMANDS_WITH_UPDATE
from core.handlers import validate_components

telegram_views = Blueprint('token_views', __name__)


def send_message(bot, text, chat_id=None):
    return bot.sendMessage(
        chat_id=chat_id or 412945234,
        text=text
    ).to_json()


@telegram_views.route(f"/{os.environ['TOKEN']}", methods=['POST'])
def webhook():
    if request.method == "POST":
        json = request.get_json()
        if not json:
            raise ValueError('No payload')

        bot = telegram.Bot(token=os.environ['TOKEN'])
        update = telegram.Update.de_json(json, bot)

        command_text, status_code = validate_components(update)

        if status_code == 1337:
            text = f'{command_text}.\nUpdate: {update.to_dict()}'
            return send_message(bot, text=text, chat_id=412945234)
        if status_code == 1338:
            query = update.callback_query
            return bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=query.message.text,
            ).to_json()

        chat_id = update.message.chat.id
        if status_code != 'valid-command':
            return send_message(bot, text=command_text, chat_id=chat_id)

        args = []
        if command_text in COMMANDS_WITH_TEXT:
            args.append(' '.join(update.message.text.split(' ')[1:]))
        elif command_text in COMMANDS_WITH_UPDATE:
            args.append(update)
        elif command_text in COMMANDS_WITH_UPDATE_AND_BOT:
            args += [update, bot]
        results = ALLOWED_COMMANDS[command_text](*args)

        try:
            send_message(bot, text=results, chat_id=chat_id)
        except telegram.error.BadRequest as err:
            text = (
                f'Restrict results (e.g. /{command_text} 3'
                if 'Message is too long' in str(err)
                else str(err)
            )
            send_message(bot, text=text, chat_id=chat_id)
        return 'completed'
    return f"Unexpected method {request.method}"
