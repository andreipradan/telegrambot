from unittest import mock

import pytest
import responses

from scrapers.clients.stirioficiale import StiriOficialeClient
from scrapers.clients.stirioficiale import get_children
from scrapers.clients.stirioficiale import parse_header
from scrapers.clients.stirioficiale import parse_sub_header
from scrapers.clients.stirioficiale import parse_text

URL = "https://stirioficiale.ro/informatii"


def test_get_children():
    elements = mock.MagicMock()
    elements.find_all.return_value = []
    get_children(elements)
    elements.find_all.assert_called_once_with(True, recursive=False)


@pytest.mark.parametrize("text", ["\nfoo", "\tfoo\n", "  foo\t", "\t\n\tfoo"])
def test_parse_text(text):
    text_mock = mock.MagicMock(text=text)
    assert parse_text(text_mock) == "foo"


def test_parse_sub_header():
    sub_header = mock.MagicMock()
    sub_header.time.find_all.return_value = [
        mock.MagicMock(text="\n\t  key  \t\n"),
        mock.MagicMock(text="val1"),
        mock.MagicMock(text="val2"),
        "val3",
    ]
    assert parse_sub_header(sub_header) == ("key", "val1 val2")


@mock.patch("scrapers.clients.stirioficiale.parse_text")
@mock.patch("scrapers.clients.stirioficiale.get_children")
def test_parse_header(children, parse_mock):
    children.side_effect = [[1, 2], [3, 4]]
    parse_mock.side_effect = [3, 4, 5]
    assert parse_header(mock.MagicMock()) == ("3 4", 5)


@mock.patch("requests.get")
@mock.patch("scrapers.clients.stirioficiale.BeautifulSoup")
class TestLatestArticle:
    @mock.patch("scrapers.clients.stirioficiale.parse_text")
    @mock.patch("scrapers.clients.stirioficiale.parse_header")
    @mock.patch("scrapers.clients.stirioficiale.get_children")
    def test_with_four_elements(self, children, header, text, *_):
        link = mock.MagicMock()
        link.a.__getitem__.return_value = "url_foo"
        children.return_value = [1, 2, 3, link]
        header.return_value = ["date_time_foo", "author_foo"]
        text.side_effect = ["title_foo", "desc_foo"]
        responses.add(responses.GET, URL)
        assert StiriOficialeClient()._fetch() == {
            "autor": "author_foo",
            "data": "date_time_foo",
            "descriere": "desc_foo",
            "titlu": "title_foo",
            "url": "url_foo",
        }

    @mock.patch(
        "scrapers.clients.stirioficiale.get_children", return_value="foo"
    )
    @responses.activate
    def test_other_number_of_elements(self, *_):
        responses.add(responses.GET, URL)
        with pytest.raises(ValueError) as e:
            StiriOficialeClient().sync()
        assert e.value.args[0] == "Invalid number of elements in article: foo"

    @mock.patch(
        "scrapers.clients.stirioficiale.parse_sub_header", return_value=[1, 2]
    )
    @mock.patch("scrapers.clients.stirioficiale.parse_text")
    @mock.patch("scrapers.clients.stirioficiale.parse_header")
    @mock.patch("scrapers.clients.stirioficiale.get_children")
    def test_with_five_elements(self, children_mock, header, text, *_):
        link = mock.MagicMock()
        link.a.__getitem__.return_value = "url_foo"
        children_mock.return_value = [1, 2, 3, 4, link]
        header.return_value = ["date_time_foo", "author_foo"]
        text.side_effect = ["title_foo", "desc_foo"]
        responses.add(responses.GET, URL)
        assert StiriOficialeClient()._fetch() == {
            1: 2,
            "autor": "author_foo",
            "data": "date_time_foo",
            "descriere": "desc_foo",
            "titlu": "title_foo",
            "url": "url_foo",
        }
