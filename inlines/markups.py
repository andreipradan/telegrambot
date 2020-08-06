from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from core import database
from core.utils import chunks

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


def get_game_markup():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    game["name"], callback_data=f"games_{game['name']}"
                )
                for game in chunk
            ]
            for chunk in chunks(
                list(database.get_many(collection="games", order_by="name")), 5
            )
        ]
        + [[InlineKeyboardButton("✅", callback_data="end")]]
    )
