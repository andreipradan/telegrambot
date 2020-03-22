import os

import telegram

from flask import Blueprint
from flask import request
from flask import url_for

from core.handlers import ALLOWED_COMMANDS
from core.handlers import COMMANDS_WITH_TEXT
from core.handlers import COMMANDS_WITH_UPDATE
from core.views.base import make_json_response

command_views = Blueprint('command_views', __name__)

home_view_name = 'command_views.command_list'


@command_views.route('/commands/')
def command_list():
    return make_json_response(
        data=[
            f"{url_for(home_view_name, _external=True)}{allowed_command}/"
            for allowed_command in ALLOWED_COMMANDS
        ]
    )


@command_views.route('/commands/<command_name>/')
def command(command_name):
    if command_name not in ALLOWED_COMMANDS:
        return make_json_response(
            home=home_view_name,
            errors=[
                f"Unknown command: '{command_name}'. "
                f"Navigate 'home' (from 'links') to see the list of commands. ",
            ]
        )

    if command_name in COMMANDS_WITH_TEXT and not request.args:
        error = (
            f"This command requires a text URL param. "
            f"e.g. {url_for(home_view_name, _external=True)}"
            f"{command_name}/?text=hello"
        )
        return make_json_response(home=home_view_name, errors=[error])

    if command_name in COMMANDS_WITH_UPDATE:
        error = (
            'This command can not be executed via http. '
            '[requires a Telegram update object]'
        )
        return make_json_response(home=home_view_name, errors=[error])

    result = ALLOWED_COMMANDS[command_name](**request.args.to_dict())

    if 'json' not in request.args:
        bot = telegram.Bot(token=os.environ['TOKEN'])
        bot.send_message(chat_id=412945234, text=result)

    return make_json_response(result, home=home_view_name)
