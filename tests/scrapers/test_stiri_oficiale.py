from unittest import mock

import pytest
import responses

from core import constants
from scrapers import stiri_oficiale


def test_get_children():
    elements = mock.MagicMock()
    elements.find_all.return_value = []
    stiri_oficiale.get_children(elements)
    elements.find_all.assert_called_once_with(True, recursive=False)


@pytest.mark.parametrize("text", ["\nfoo", "\tfoo\n", "  foo\t", "\t\n\tfoo"])
def test_parse_text(text):
    text_mock = mock.MagicMock(text=text)
    assert stiri_oficiale.parse_text(text_mock) == "foo"


def test_parse_sub_header():
    sub_header = mock.MagicMock()
    sub_header.time.find_all.return_value = [
        mock.MagicMock(text="\n\t  key  \t\n"),
        mock.MagicMock(text="val1"),
        mock.MagicMock(text="val2"),
        "val3",
    ]
    assert stiri_oficiale.parse_sub_header(sub_header) == ("key", "val1 val2")


@mock.patch("scrapers.stiri_oficiale.parse_text")
@mock.patch("scrapers.stiri_oficiale.get_children")
def test_parse_header(get_children, parse_text):
    get_children.side_effect = [[1, 2], [3, 4]]
    parse_text.side_effect = [3, 4, 5]
    assert stiri_oficiale.parse_header(mock.MagicMock()) == ("3 4", 5)


@mock.patch("scrapers.stiri_oficiale.BeautifulSoup")
class TestLatestArticle:
    @mock.patch("scrapers.stiri_oficiale.parse_text")
    @mock.patch("scrapers.stiri_oficiale.parse_header")
    @mock.patch("scrapers.stiri_oficiale.get_children")
    def test_with_four_elements(self, get_children, header, text, _):
        link = mock.MagicMock()
        link.a.__getitem__.return_value = "url_foo"
        get_children.return_value = [1, 2, 3, link]
        header.return_value = ["date_time_foo", "author_foo"]
        text.side_effect = ["title_foo", "desc_foo"]
        responses.add(responses.GET, constants.URLS["stiri-oficiale"])
        assert stiri_oficiale.latest_article(json=True) == {
            "autor": "author_foo",
            "data": "date_time_foo",
            "descriere": "desc_foo",
            "titlu": "title_foo",
            "url": "url_foo",
        }

    @mock.patch("scrapers.stiri_oficiale.parse_text")
    @mock.patch(
        "scrapers.stiri_oficiale.parse_sub_header", return_value=[1, 2]
    )
    @mock.patch("scrapers.stiri_oficiale.parse_header")
    @mock.patch("scrapers.stiri_oficiale.get_children")
    def test_with_five_elements(self, get_children, header, sub, text, _):
        link = mock.MagicMock()
        link.a.__getitem__.return_value = "url_foo"
        get_children.return_value = [1, 2, 3, 4, link]
        header.return_value = ["date_time_foo", "author_foo"]
        text.side_effect = ["title_foo", "desc_foo"]
        responses.add(responses.GET, constants.URLS["stiri-oficiale"])
        assert stiri_oficiale.latest_article(json=True) == {
            1: 2,
            "autor": "author_foo",
            "data": "date_time_foo",
            "descriere": "desc_foo",
            "titlu": "title_foo",
            "url": "url_foo",
        }

    @mock.patch("scrapers.stiri_oficiale.get_children", return_value="foo")
    @responses.activate
    def test_other_number_of_elements(self, *_):
        responses.add(responses.GET, constants.URLS["stiri-oficiale"])
        with pytest.raises(ValueError) as e:
            stiri_oficiale.latest_article()
        assert e.value.args[0] == "Invalid number of elements in article: foo"

    @mock.patch("scrapers.stiri_oficiale.parse_text")
    @mock.patch(
        "scrapers.stiri_oficiale.parse_sub_header", return_value=[1, 2]
    )
    @mock.patch("scrapers.stiri_oficiale.parse_header")
    @mock.patch("scrapers.stiri_oficiale.get_children")
    @mock.patch("scrapers.formatters.parse_global")
    def test_with_five_elements_formatted(
        self, glob, get_children, header, sub, text, _
    ):
        glob.return_value = "results"
        link = mock.MagicMock()
        link.a.__getitem__.return_value = "url_foo"
        get_children.return_value = [1, 2, 3, 4, link]
        header.return_value = ["date_time_foo", "author_foo"]
        text.side_effect = ["title_foo", "desc_foo"]
        responses.add(responses.GET, constants.URLS["stiri-oficiale"])
        assert stiri_oficiale.latest_article() == "results"
        glob.assert_called_once_with(
            title="🔵 title_foo",
            stats={1: 2, "autor": "author_foo", "data": "date_time_foo",},
            items={"desc_foo": ["url_foo"]},
            emoji="❗",
        )
