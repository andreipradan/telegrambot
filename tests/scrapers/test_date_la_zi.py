from unittest import mock

import pytest
import requests
import responses

from scrapers import date_la_zi

URL = "https://api1.datelazi.ro/api/v2/data/ui-data/"


def get_payload(**kwargs):
    return {
        "ageHistogram": {"histogram": []},
        "genderStats": {
            "percentageOfMen": 1,
            "percentageOfWomen": 2,
            "percentageOfChildren": 3,
        },
        "quickStats": {
            "totals": {
                "last_updated": 1,
                "date": 1234,
                "date_string": "dates",
            },
            "history": [{"date_string": "mar 2, 2020", "date": 4, "foo": "f"}],
            "last_updated_on_string": "jun 3, 1234",
        },
        "lastDataUpdateDetails": {"last_updated_on_string": 3},
    }


def mock_request(**kwargs):
    responses.add(
        responses.GET,
        URL,
        status=kwargs.pop("status_code", 200),
        json=get_payload(**kwargs),
    )


class DateLaZiMixin:
    func = NotImplemented

    @responses.activate
    @pytest.mark.parametrize("status", [401, 403, 404, 405, 500, 504])
    def test_bad_status_code(self, status):
        mock_request(status_code=status)
        with pytest.raises(requests.exceptions.HTTPError) as e:
            getattr(date_la_zi, self.func)()
        assert str(status) in e.value.args[0]


class TestHistogram(DateLaZiMixin):
    func = "histogram"

    @responses.activate
    def test_json(self):
        mock_request()
        results = get_payload()
        results["quickStats"]["totals"].pop("date")
        results["quickStats"]["totals"].pop("date_string")
        assert date_la_zi.histogram(json=True) == results

    @responses.activate
    @mock.patch("scrapers.formatters.parse_global", return_value="parse_foo")
    def test_formatted(self, parse_global):
        mock_request()
        assert date_la_zi.histogram() == "parse_foo"
        parse_global.assert_called_once_with(
            title="🦠 Romania",
            stats={"last_updated": 1},
            items={
                "Dupa varsta": [],
                "Dupa gen (%)": {"barbati": 1, "femei": 2, "copii": 3,},
            },
            footer="\nLast updated: 3",
        )


class TestHistory(DateLaZiMixin):
    func = "history"

    @responses.activate
    def test_json(self):
        mock_request()
        assert date_la_zi.history(json=True) == get_payload()

    @responses.activate
    @mock.patch("scrapers.formatters.parse_global", return_value="parse_foo")
    def test_formatted(self, parse_global):
        mock_request()
        assert date_la_zi.history() == "parse_foo"
        parse_global.assert_called_once_with(
            title="🦠 Romania istoric",
            stats={"Last updated": "jun 3, 1234"},
            items={"Mar 2, 2020": {"foo": "f"}},
            footer="\nLast updated: 3",
            emoji="📅",
        )
