import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from commands.covid import get_romania_stats

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update):
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("covid", callback_data='romania'),
            InlineKeyboardButton("counties", callback_data='judete'),
            InlineKeyboardButton("end", callback_data='end'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return update.message.reply_text(
        "Start handler, Choose an option",
        reply_markup=reply_markup
    ).to_json()


def end(query):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    return query.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="See you next time!"
    ).to_json()


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

