import os

import telegram

from flask import Blueprint
from flask import abort
from flask import request
from flask import url_for

import commands
from core import inline, constants
from core.constants import IDS
from core.handlers import validate_components
from core.views.base import make_json_response


command_views = Blueprint('command_views', __name__)

home_view_name = 'command_views.command_list'


@command_views.route('/commands/')
def command_list():
    return make_json_response(
        data=[
            f"{url_for(home_view_name, _external=True)}{allowed_command}/"
            for allowed_command in constants.COMMANDS_FOR_VIEWS
        ]
    )


@command_views.route('/commands/<command_name>/')
def command(command_name):
    if command_name not in constants.COMMANDS_FOR_VIEWS:
        return make_json_response(
            home=home_view_name,
            errors=[
                f"Unknown command: '{command_name}'. "
                f"Navigate 'home' (from 'links') to see the list of commands. ",
            ]
        )

    if command_name in constants.COMMANDS_WITH_TEXT and not request.args:
        error = (
            f"This command requires a text URL param. "
            f"e.g. {url_for(home_view_name, _external=True)}"
            f"{command_name}/?text=hello"
        )
        return make_json_response(home=home_view_name, errors=[error])

    if command_name in constants.COMMANDS_WITH_UPDATE:
        error = (
            'This command can not be executed via http. '
            '[requires a Telegram update object]'
        )
        return make_json_response(home=home_view_name, errors=[error])

    result = getattr(commands, command_name)(**request.args.to_dict())

    if 'telegram' in request.args:
        bot = telegram.Bot(token=os.environ['TOKEN'])
        bot.send_message(chat_id=412945234, text=result)

    return make_json_response(result, home=home_view_name)


def send_message(bot, text, chat_id=None):
    return bot.send_message(
        chat_id=chat_id or IDS['ap'],
        text=text
    ).to_json()


@command_views.route(f"/{os.environ['TOKEN']}", methods=['POST'])
def webhook():
    if request.method == "POST":
        json = request.get_json()
        if not json:
            raise ValueError('No payload')

        bot = telegram.Bot(token=os.environ['TOKEN'])
        update = telegram.Update.de_json(json, bot)

        if update.callback_query:
            data = update.callback_query.data
            if data == 'end':
                return inline.end(update)
            elif data == 'more':
                return inline.more(update)
            elif data == 'back':
                return inline.restart(update)
            return inline.refresh_data(update, getattr(commands, data)())

        command_text, status_code = validate_components(update)

        if status_code == 1337:
            if command_text == 'skip-debug':
                return 'ok'
            text = f'{command_text}.\nUpdate: {update.to_dict()}'
            return send_message(bot, text=text, chat_id=IDS['ap'])

        chat_id = update.message.chat.id
        if status_code != 'valid-command':
            return send_message(bot, text=command_text, chat_id=chat_id)

        args = []
        if command_text in constants.COMMANDS_WITH_TEXT:
            args.append(' '.join(update.message.text.split(' ')[1:]))
        elif command_text in constants.COMMANDS_WITH_UPDATE:
            args.append(update)

        if command_text == 'start':
            return inline.start(update)

        results = getattr(commands, command_text)(*args)

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


@command_views.route(f"/reset-webhook/")
def reset_webhook():
    bot = telegram.Bot(token=os.environ['TOKEN'])
    if request.args.get('key', None) != '@aoleu_bot':
        abort(403)
    bot.deleteWebhook()
    url = url_for('command_views.webhook', _external=True).replace('http://', 'https://')
    return f"Result: {bot.setWebhook(url)}"
