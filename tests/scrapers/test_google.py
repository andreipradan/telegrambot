from unittest import mock

import pytest
from google.api_core.exceptions import InvalidArgument

from scrapers import google


class TestAnalyzeSentiment:
    @staticmethod
    def mock_sentence(**kwargs):
        sentence = mock.MagicMock()
        sentence.text.content = kwargs.get('content', "foo_content")
        sentence.sentiment.score = kwargs.get('score', 1)
        sentence.sentiment.magnitude = kwargs.get('magnitude', 2)
        return sentence

    def mock_analyze(self):
        resp = mock.MagicMock()
        resp.document_sentiment.score = 1
        resp.document_sentiment.magnitude = 2
        resp.language = 3
        resp.sentences = [
            self.mock_sentence(score=x, magnitude=x+1) for x in range(5, 7)
        ]
        return resp

    def test_with_no_text(self):
        assert google.analyze_sentiment("") == (
            "Syntax: /analyze_sentiment <your text here>"
        )

    @mock.patch("scrapers.google.language_v1.LanguageServiceClient")
    def test_invalid_argument(self, lang):
        lang.return_value.analyze_sentiment.side_effect = InvalidArgument("fo")
        assert google.analyze_sentiment("foo") == "fo"

    @mock.patch("scrapers.google.language_v1.LanguageServiceClient")
    def test_json(self, lang):
        resp = self.mock_analyze()
        lang.return_value.analyze_sentiment.return_value = resp
        assert google.analyze_sentiment("foo", json=True) == {
            'Language': 3,
            'Overall magnitude': 2,
            'Overall score': 1,
            'sentences': {
                'foo_content': {
                    'Score': 6,
                    'Magnitute': 7
                }
            }
        }

    @mock.patch("scrapers.google.parse_global", return_value="parsed")
    @mock.patch("scrapers.google.language_v1.LanguageServiceClient")
    def test_formatted(self, lang, parser):
        resp = self.mock_analyze()
        lang.return_value.analyze_sentiment.return_value = resp
        assert google.analyze_sentiment("foo") == "parsed"
        parser.assert_called_once_with(
            title="💔 Sentiment analysis",
            stats={'Language': 3, 'Overall magnitude': 2, 'Overall score': 1},
            items={
                'foo_content': {
                    'Score': 6,
                    'Magnitute': 7
                }
            },
            footer="""===================================
Clearly Positive:   "score": 0.8,  "magnitude": 3.0
Clearly Negative: "score": -0.6, "magnitude": 4.0
Neutral:                 "score": 0.1,  "magnitude": 0.0
Mixed:                   "score": 0.0,  "magnitude": 4.0
"""
        )
