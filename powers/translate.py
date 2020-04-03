import logging

import six
from google.api_core.exceptions import GoogleAPICallError

from google.cloud import translate_v2 as translate
from google.cloud.exceptions import BadRequest

from scrapers.formatters import parse_global

logger = logging.getLogger(__name__)

EXAMPLES = {
    "Examples": [
        "/translate ce faci mai tarziu?",
        "/translate target=fr jeg spiser et eple",
    ],
}

HELP_TEXT = {
    "Usage": [
        "/translate <insert text here>",
        "/translate target=<language_code> <insert text here>",
        "/translate languages",
    ],
    **EXAMPLES
}

MISSING_TARGET = "  Please provide a valid target language."
MISSING_TEXT = "️ Please provide a text to translate."
TYPE_HELP = {
    "For more usages": ' /translate help '
}


def translate_text(text):
    if len(text) > 255:
        return f"Too many characters. Try sending less than 255 characters"

    if not text.strip():
        return parse_global(TYPE_HELP, EXAMPLES, MISSING_TEXT)
    if text == "help":
        return parse_global(
            ["Usage", "Examples"], HELP_TEXT, "Translate guide"
        )
    if text == "languages":
        return "https://cloud.google.com/translate/docs/languages"

    kwargs = text.split(" ")[0].split("=")
    if len(kwargs) == 2 and kwargs[0] == "target":
        if not kwargs[1]:
            return parse_global(TYPE_HELP, EXAMPLES, MISSING_TARGET)

        target = kwargs[1]
        text = " ".join(text.split(" ")[1:])
        if not text.strip():
            return parse_global(TYPE_HELP, EXAMPLES, MISSING_TEXT)
    else:
        target = "en"

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    try:
        result = translate_client.translate(
            text, target_language=target, format_="text"
        )
    except (GoogleAPICallError, BadRequest) as e:
        logger.error(e)
        return "Something went wrong. For usage and examples type '/translate help'."

    return parse_global(
        title="💬 Translate",
        stats={
            "Source text": result["input"],
            "Source language": result["detectedSourceLanguage"],
            "Translation": result["translatedText"],
        },
        items={},
    )
