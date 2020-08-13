from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from core import database
from core.utils import chunks
from powers.games import Games

COVID = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🇷🇴", callback_data="local_quick_stats"),
            InlineKeyboardButton("🏙", callback_data="local_counties"),
            InlineKeyboardButton("👵", callback_data="local_age"),
            InlineKeyboardButton("🌎", callback_data="local_global_stats"),
            InlineKeyboardButton("🗞", callback_data="local_latest_article"),
            InlineKeyboardButton("📊", callback_data="datelazi"),
            InlineKeyboardButton("✅", callback_data="end"),
        ]
    ]
)
MORE = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("⬅️", callback_data="back"),
            InlineKeyboardButton("✅", callback_data="end"),
        ]
    ]
)


def get_game_markup(chat_id):
    games = Games.get_list(chat_id=chat_id)
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    game["name"], callback_data=f"games_{game['name']}"
                )
                for game in chunk
            ]
            for chunk in chunks(list(games), 5)
        ]
        + [[InlineKeyboardButton("✅", callback_data="end")]]
    )
