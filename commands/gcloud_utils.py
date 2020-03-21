from collections import OrderedDict

from google.cloud import language_v1
from google.cloud.language_v1 import enums
from google.api_core.exceptions import InvalidArgument

from commands.utils import parse_global


def get_footer():
    return """===================================
    Clearly Positive:   "score": 0.8,  "magnitude": 3.0
    Clearly Negative: "score": -0.6, "magnitude": 4.0
    Neutral:                 "score": 0.1,  "magnitude": 0.0
    Mixed:                   "score": 0.0,  "magnitude": 4.0
    ===================================
    """


def analyze_sentiment(text):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    if not text:
        return 'Syntax: /analyze_sentiment <your text here>'

    client = language_v1.LanguageServiceClient()

    # Available types: PLAIN_TEXT, HTML
    document = {"content": text, "type": enums.Document.Type.PLAIN_TEXT}
    encoding_type = enums.EncodingType.UTF8
    try:
        response = client.analyze_sentiment(document, encoding_type=encoding_type)
    except InvalidArgument as error:
        return error.message

    top_stats = OrderedDict()
    top_stats['Overall score'] = response.document_sentiment.score
    top_stats['Overall magnitude'] = response.document_sentiment.magnitude
    top_stats['Language'] = response.language

    sentences = {}
    for sentence in response.sentences:
        title = sentence.text.content
        sentences[title] = OrderedDict()
        sentences[title]['Score'] = sentence.sentiment.score
        sentences[title]['Magnitute'] = sentence.sentiment.magnitude
    return parse_global(
        '💔 Sentiment analysis',
        top_stats=top_stats,
        items=sentences,
        footer=get_footer(),
    )
