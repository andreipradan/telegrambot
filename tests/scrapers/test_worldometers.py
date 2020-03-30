from unittest import mock

import pytest
import responses

from core import constants
from scrapers import global_


class TestGlobal:
    def test_invalid_count(self):
        assert global_("a") == 'Invalid count: "a".'

    @pytest.mark.parametrize("with_json", [True, False])
    @responses.activate
    @mock.patch("scrapers.formatters.parse_global")
    @mock.patch("scrapers.worldometers.BeautifulSoup")
    def test_parse(self, soup, parser, with_json):
        responses.add(responses.GET, constants.URLS["worldometers"])
        element = mock.MagicMock()
        element.h1.text = "key_foo"
        element.div.span.text.strip.return_value = "value_foo"
        soup().find_all.return_value = [element]
        row = mock.MagicMock()
        row.select().__iter__.return_value = [
            mock.MagicMock(text="country_foo")
        ]
        soup().select().__getitem__.return_value = [row]

        if with_json:
            assert global_(json=True) == {
                "top_stats": {
                    "key_foo": "value_foo",
                    "last_updated": mock.ANY,
                },
                "countries": {"country_foo": {}},
            }
        else:
            parser.return_value = "parsed"
            assert global_(3) == "parsed"
            parser.assert_called_once_with(
                title="🌎 Global Stats",
                stats={"key_foo": "value_foo"},
                items={"country_foo": {}},
                emoji="🦠",
                footer=f"({soup().find()})\n[Source: worldometers.info]",
            )
