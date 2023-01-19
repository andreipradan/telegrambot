import os

ALLOWED_COMMANDS = [
    "analyze_sentiment",
    "chatgpt",
    "games",
    "bus",
    "get_chat_id",
    "randomize",
    "save",
    "saved",
    "start",
    "translate",
]
DATE_FORMAT = "%Y-%m-%d"
GAME_COMMANDS = [
    "games",
    "randomize",
]
GOOGLE_CLOUD_COMMANDS = [
    "analyze_sentiment",
    "translate",
]

GOOGLE_CLOUD_WHITELIST = {
    "group": os.getenv("GOOGLE_GROUP_WHITELIST", "").split(","),
    "supergroup": os.getenv("GOOGLE_SUPERGROUP_WHITELIST", "").split(","),
    "private": os.getenv("GOOGLE_PRIVATE_WHITELIST", "").split(","),
}

COLLECTION = {
    "archive": "romania-archive",
    "archive-small": "romania-archive-small",
    "country": "country-collection",
    "global": "global-collection",
    "romania": "romania-collection",
}
SLUG = {
    "global": "global-slug",
    "romania": "romania-slug",
    "stiri-oficiale": "stiri-oficiale-slug",
}

WEBHOOK_WHITELIST = ["91.108.4.0/22", "149.154.160.0/20"]  # telegram networks
