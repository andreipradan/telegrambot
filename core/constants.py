import os

ALLOWED_COMMANDS = [
    "analyze_sentiment",
    "start",
    "translate",
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
    "country": "country-collection",
    "global": "global-collection",
    "romania": "romania-collection",
}
SLUG = {
    "global": "global-slug",
    "romania": "romania-slug",
    "stiri-oficiale": "stiri-oficiale-slug",
}

CHAT_ID = os.environ["CHAT_ID"]
DEBUG_CHAT_ID = os.getenv("DEBUG_CHAT_ID", CHAT_ID)
TOKEN = os.environ["TOKEN"]
