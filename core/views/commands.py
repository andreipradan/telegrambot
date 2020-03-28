from flask import Blueprint
from flask import request
from flask import url_for

import scrapers
from core import constants
from core.views.base import make_json_response

commands_views = Blueprint("commands_views", __name__)

home_view_name = "commands_views.command_list"


@commands_views.route("/commands/")
def command_list():
    return make_json_response(
        data=[
            f"{url_for(home_view_name, _external=True)}{allowed_command}/"
            for allowed_command in constants.COMMANDS_FOR_VIEWS
        ]
    )


@commands_views.route("/commands/<command_name>/")
def command(command_name):
    if command_name not in constants.COMMANDS_FOR_VIEWS:
        error = (
            f"Unknown command: '{command_name}'. "
            f"Navigate 'home' (from 'links') to see the list of commands."
        )
        return make_json_response(home=home_view_name, errors=[error],)

    if command_name in constants.COMMANDS_WITH_TEXT and not request.args:
        error = (
            f"This command requires a text URL param. "
            f"e.g. {url_for(home_view_name, _external=True)}"
            f"{command_name}/?text=hello"
        )
        return make_json_response(home=home_view_name, errors=[error])

    return make_json_response(
        getattr(scrapers, command_name)(json=True, **request.args.to_dict()),
        home=home_view_name,
    )
