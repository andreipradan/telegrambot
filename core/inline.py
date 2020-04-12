import logging

import telegram
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

START_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🇷🇴", callback_data="local_quick_stats"),
            InlineKeyboardButton("🏙", callback_data="local_counties"),
            InlineKeyboardButton("👵", callback_data="local_age"),
            InlineKeyboardButton("🌎", callback_data="local_global_stats"),
            InlineKeyboardButton("🗞", callback_data="local_latest_article"),
            InlineKeyboardButton("📊", callback_data="datelazi"),
        ]
        + [InlineKeyboardButton("✅", callback_data="end")]
    ]
)


MORE_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("⬅️", callback_data="back"),
            InlineKeyboardButton("✅", callback_data="end"),
        ]
    ]
)


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
            reply_markup=MORE_MARKUP,
        ).to_json()
    except telegram.error.BadRequest as e:
        return e.message


def refresh_data(update, command):
    bot = update.callback_query.bot
    message = update.callback_query.message
    try:
        return bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text=command + "\n" + "\t" * 50,
            reply_markup=message.reply_markup,
            disable_web_page_preview=command != "https://datelazi.ro",
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).to_json()
    except telegram.error.BadRequest as e:
        return e.message


def back(update):
    """Prompt same text & keyboard as `start` does but not as new message"""
    bot = update.callback_query.bot
    message = update.callback_query.message

    try:
        return bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text="Hello! Choose an option",
            reply_markup=START_MARKUP,
        ).to_json()
    except telegram.error.BadRequest as e:
        return e.message


def start(update):
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    return update.message.reply_text(
        "Hello! Choose an option", reply_markup=START_MARKUP
    ).to_json()
