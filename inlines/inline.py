import logging

import telegram

from inlines import markups

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def back(update):
    """Prompt same text & keyboard as `start` does but not as new message"""
    bot = update.callback_query.bot
    message = update.callback_query.message

    try:
        return bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text="Hello! Choose an option",
            reply_markup=markups.COVID,
        ).to_json()
    except telegram.error.BadRequest as e:
        return e.message


def end(update):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    bot = update.callback_query.bot
    message = update.callback_query.message
    try:
        return bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text="See you next time!",
        ).to_json()
    except telegram.error.BadRequest as e:
        return e.message


def more(update):
    bot = update.callback_query.bot
    message = update.callback_query.message

    try:
        return bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text="Choose an option",
            reply_markup=markups.MORE,
        ).to_json()
    except telegram.error.BadRequest as e:
        return e.message


def refresh_data(update, text):
    bot = update.callback_query.bot
    message = update.callback_query.message
    text = text.replace("_", "\\_")

    try:
        return bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text=text + "\n" + "\t" * 50,
            reply_markup=message.reply_markup,
            disable_web_page_preview=text != "https://datelazi.ro",
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).to_json()
    except telegram.error.BadRequest as e:
        return e.message


def start(update, games=False):
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    return update.message.reply_text(
        "Hello! Choose an option",
        reply_markup=markups.COVID if not games else markups.get_game_markup(),
    ).to_json()
