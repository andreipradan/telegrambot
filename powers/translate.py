import logging

import six
from google.api_core.exceptions import GoogleAPICallError

from google.cloud import translate_v2 as translate
from google.cloud.exceptions import BadRequest

from scrapers.formatters import parse_global

logger = logging.getLogger(__name__)


def get_help_text():
    return """
Usages:
- /translate <insert text here>
- /translate target=<language_code> <insert text here>
Supported language codes: https://cloud.google.com/translate/docs/languages

Examples:
- /translate ce faci mai tarziu?
- /translate target=de jeg spiser et eple
"""


def translate_text(text):
    if len(text) > 255:
        return f"Too many characters. Try sending less than 255 characters"

    if not text.strip():
        return """
Please provide a valid text to translate.
Type "/translate help" for usages.
"""

    if text == "help":
        return get_help_text()

    kwargs = text.split(" ")[0].split("=")
    if len(kwargs) == 2 and kwargs[0] == "target":
        if not kwargs[1]:
            return """
Please provide a valid target language.
Type "/translate help" for usages.
"""
        target = kwargs[1]
        text = " ".join(text.split(" ")[1:])
        if not text.strip():
            return """
Please provide a valid text to translate.
Type "/translate help" for usages.
"""
    else:
        target = "en"

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    try:
        result = translate_client.translate(text, target_language=target)
    except (GoogleAPICallError, BadRequest) as e:
        logger.error(e)
        return "Something went wrong. For Usages type '/translate help'."

    return parse_global(
        title="💬 Translate",
        stats={
            "Input": result["input"],
            "Source language": result["detectedSourceLanguage"],
            "Translation": result["translatedText"],
        },
        items={},
    )
