import os

import telegram

from flask import Blueprint
from flask import request

from core import inline
from core import handlers
from core import local_data
from core import utils
from core.constants import GAME_COMMANDS
from core.constants import GOOGLE_CLOUD_COMMANDS
from core.constants import GOOGLE_CLOUD_WHITELIST
from powers.analyze_sentiment import analyze_sentiment
from powers.games import Games
from powers.translate import translate_text
from scrapers.formatters import parse_global

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

    if command_text in GAME_COMMANDS:
        user_id = str(update.message.from_user.id)
        if user_id not in GOOGLE_CLOUD_WHITELIST["private"]:
            return utils.send_message(bot, "Unauthorized", chat_id)

        if command_text == "games":
            args = update.message.text.split(" ")[1:]
            if not args:
                return utils.send_message(bot, Games.get_list(), chat_id)
            if len(args) not in (1, 2, 3) or args[0] == "help":
                return utils.send_message(
                    bot,
                    parse_global(
                        title="Syntax",
                        stats=[
                            "/games",
                            "/games <game_name> => shows score of <game_name>",
                            "/games <game_name> new => creates a new game",
                            "/games <game_name> new_player <player_name>"
                            " => add new player",
                            "/games <game_name> + <player_name>"
                            " => increase <player_name>'s score by 1",
                            "/games <game_name> - <player_name>"
                            " => decrease <player_name>'s score by 1",
                        ],
                        items={},
                    ),
                    chat_id,
                )
            name, *args = args
            games = Games(name)
            if not args:
                return utils.send_message(bot, games.get(), chat_id)
            if len(args) == 1:
                return utils.send_message(bot, games.new_game(), chat_id)
            return utils.send_message(bot, games.update(*args), chat_id)

    raise ValueError(f"Unhandled command: {command_text}, {status_code}")
