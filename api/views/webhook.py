import logging
import os
import random

from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import exceptions
from google.cloud import translate_v2 as translate

import six
import telegram

from flask import Blueprint
from flask import request

from core import handlers
from core import local_data
from core import utils
from core.constants import GAME_COMMANDS
from core.constants import GOOGLE_CLOUD_COMMANDS
from core.constants import GOOGLE_CLOUD_WHITELIST
from inlines import inline
from powers.analyze_sentiment import analyze_sentiment
from powers.games import Games
from powers.translate import translate_text
from scrapers.formatters import parse_global

webhook_views = Blueprint("webhook_views", __name__)

TOKEN = os.environ["TOKEN"]
TRANSLATE_BOT_TOKEN = os.environ["TRANSLATE_BOT_TOKEN"]
TRANSLATE_BOT_WHITELIST = os.environ["TRANSLATE_BOT_WHITELIST"].split(",")
TRANSLATE_BOT_WHITELIST.append("andreierdna")
try:
    TRANSLATE_BOT_TEXT_MAX_SIZE = int(
        os.getenv("TRANSLATE_BOT_TEXT_MAX_SIZE", 800)
    )
except (TypeError, ValueError):
    TRANSLATE_BOT_TEXT_MAX_SIZE = 800


@webhook_views.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    json = request.get_json()
    if not json:
        raise ValueError("No payload")

    bot = telegram.Bot(token=TOKEN)
    update = telegram.Update.de_json(json, bot)

    command_text, status_code = handlers.validate_components(update)

    if command_text == "inline":
        chat_id = update.callback_query.message.chat_id
        if status_code in ["more", "back", "end"]:
            return getattr(inline, status_code)(update)
        if status_code.startswith("games_"):
            status_code = status_code.replace("games_", "")
            return inline.refresh_data(
                update, Games(chat_id, status_code).get()
            )
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

    if command_text == "games" and not update.message.text.split(" ")[1:]:
        return inline.start(update, games=True)

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
        chat_type = update.message.chat.type
        if str(chat_id) not in GOOGLE_CLOUD_WHITELIST[chat_type]:
            return utils.send_message(bot, "Unauthorized", chat_id)

        if command_text == "games":
            args = update.message.text.split(" ")[1:]
            if len(args) not in (2, 3) or len(args) == 2 and args[1] != "new":
                return utils.send_message(
                    bot,
                    parse_global(
                        title="Syntax",
                        stats=[
                            "/games => scores",
                            "/games <game_name> new => new game",
                            "/games <game_name> new_player <player_name>"
                            " => new player",
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
            games = Games(chat_id, name)
            if len(args) == 1:
                return utils.send_message(bot, games.new_game(), chat_id)
            return utils.send_message(bot, games.update(*args), chat_id)

        if command_text == "randomize":
            args = update.message.text.split(" ")[1:]
            if len(args) not in range(2, 51):
                return utils.send_message(
                    bot,
                    "Must contain a list of 2-50 items separated by space",
                    chat_id,
                )
            random.shuffle(args)
            return utils.send_message(
                bot,
                "\n".join(f"{i+1}. {item}" for i, item in enumerate(args)),
                chat_id,
            )
    raise ValueError(f"Unhandled command: {command_text}, {status_code}")


@webhook_views.route(f"/translate-bot/{TRANSLATE_BOT_TOKEN}", methods=["POST"])
def translate_bot():
    if request.method != "POST":
        logging.warning(f"Got {request.method} request!")
        return ""

    json = request.get_json()

    if not json:
        logging.warning("Got no json")
        return ""

    bot = telegram.Bot(token=TRANSLATE_BOT_TOKEN)

    update = telegram.Update.de_json(json, bot)
    message = update.message

    if not hasattr(message, "text"):
        logging.warning(f"got no text")
        return "No message text"

    text = message.text
    if text and message.from_user.username not in TRANSLATE_BOT_WHITELIST:
        logging.error(f"Ignoring message from: {message.from_user.username}")
        return ""

    if not message.forward_date:
        logging.warning("Ignoring message, not a forward")
        return ""

    text = text or update.message.caption
    if not text:
        logging.warning("No text nor caption provided")
        return ""

    text_size = len(text)
    if text_size > TRANSLATE_BOT_TEXT_MAX_SIZE:
        logging.warning(
            f"Exceeded {TRANSLATE_BOT_TEXT_MAX_SIZE} characters: {text_size}"
        )
        return bot.send_message(
            chat_id=message.chat_id,
            text=f"Too many characters. Try sending less than {TRANSLATE_BOT_TEXT_MAX_SIZE} characters",
        ).to_json()

    if not text.strip():
        logging.warning(f"No text after stripping: {text}")
        return ""

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    try:
        translate_client = translate.Client()
    except DefaultCredentialsError as e:
        logging.error(e)
        return ""
    try:
        result = translate_client.translate(
            text, target_language="en", format_="text"
        )
    except (GoogleAPICallError, exceptions.BadRequest) as e:
        logging.error(e)
        return "Something went wrong. For usage and examples type '/translate help'."

    detected_language = result["detectedSourceLanguage"] or ""
    return bot.send_message(
        chat_id=message.chat_id,
        text=f"[{detected_language}] {result['translatedText']}",
    ).to_json()
