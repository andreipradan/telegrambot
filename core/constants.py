import os

ALLOWED_COMMANDS = [
    "analyze_sentiment",
    "start",
]
COMMANDS_FOR_VIEWS = [
    "analyze_sentiment",
    "histogram",
    "latest_article",
]
COMMANDS_WITH_TEXT = [
    "analyze_sentiment",
]
COMMANDS_WITH_UPDATE = [
    "start",
]

DEFAULT_DB = "telegrambot_db"
COLLECTION = {
    "country": "country-collection",
    "etag": "etag-collection",
    "global": "global-collection",
    "romania": "romania-collection",
}
SLUG = {
    "etag": "etag-slug",
    "global": "global-slug",
    "romania": "romania-slug",
    "stiri-oficiale": "stiri-oficiale-slug",
}

CHAT_ID = os.environ["CHAT_ID"]
DEBUG_CHAT_ID = os.getenv("DEBUG_CHAT_ID", CHAT_ID)
TOKEN = os.environ["TOKEN"]
