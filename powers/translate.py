import logging

import six
from google.api_core.exceptions import GoogleAPICallError

from google.cloud import translate_v2 as translate

from scrapers.formatters import parse_global

logger = logging.getLogger(__name__)


def translate_text(text, target="en", limit=255):
    if len(text) > limit:
        return f"Too many characters. Try sending < {limit}"

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    try:
        result = translate_client.translate(text, target_language=target)
    except GoogleAPICallError as e:
        logger.error(e)
        return "Something went wrong."

    return parse_global(
        title="💬 Translate",
        stats={
            "Input": result["input"],
            "Detected source language": result["detectedSourceLanguage"],
            "Translation": result["translatedText"],
        },
        items={},
    )
