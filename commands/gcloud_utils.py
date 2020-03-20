from google.cloud import language_v1
from google.cloud.language_v1 import enums


def analyze_sentiment(update):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    text_content = ' '.join(update.message.text.split(' ')[1:])
    if not text_content:
        return 'Syntax: /analyze_sentiment <your text here>'

    client = language_v1.LanguageServiceClient()

    # text_content = 'I am so happy and joyful.'

    # Available types: PLAIN_TEXT, HTML
    type_ = enums.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = enums.EncodingType.UTF8

    response = client.analyze_sentiment(document, encoding_type=encoding_type)
    # Get overall sentiment of the input document
    per_sentence = '{}'.format('\n\n'.join([
        f'"{sentence.text.content}"'
        f'\n\tScore:         \t{sentence.sentiment.score}'
        f'\n\tMagnitude: \t{sentence.sentiment.magnitude}'
        for sentence in response.sentences
    ]))
    return f"""
Total sentiment score:     {response.document_sentiment.score}
Total sentiment magnitude: {response.document_sentiment.magnitude}
Language: {response.language}

{per_sentence}
"""
