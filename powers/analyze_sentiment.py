from collections import OrderedDict

from google.cloud import language_v1
from google.api_core.exceptions import InvalidArgument

from scrapers.formatters import parse_global


def get_footer():
    return """===================================
Clearly Positive:   "score": 0.8,  "magnitude": 3.0
Clearly Negative: "score": -0.6, "magnitude": 4.0
Neutral:                 "score": 0.1,  "magnitude": 0.0
Mixed:                   "score": 0.0,  "magnitude": 4.0
"""


def analyze_sentiment(text, **kwargs):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    if not text:
        return "Syntax: /analyze_sentiment <your text here>"

    client = language_v1.LanguageServiceClient()

    # Available types: PLAIN_TEXT, HTML
    doc = {"content": text, "type": language_v1.Document.Type.PLAIN_TEXT}
    encoding_type = language_v1.EncodingType.UTF8
    try:
        response = client.analyze_sentiment(doc, encoding_type=encoding_type)
    except InvalidArgument as error:
        return error.message

    stats = OrderedDict()
    stats["Overall score"] = response.document_sentiment.score
    stats["Overall magnitude"] = response.document_sentiment.magnitude
    stats["Language"] = response.language

    sentences = {}
    for sentence in response.sentences:
        title = sentence.text.content
        sentences[title] = OrderedDict()
        sentences[title]["Score"] = sentence.sentiment.score
        sentences[title]["Magnitute"] = sentence.sentiment.magnitude

    if "json" in kwargs:
        return {"sentences": sentences, **stats}

    return parse_global(
        title="💔 Sentiment analysis",
        stats=stats,
        items=sentences,
        footer=get_footer(),
    )
