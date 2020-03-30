from unittest import mock

import pytest
from flask import url_for

from core.views import new_cases


class BaseNewCasesMixin:
    db_stats_kwargs = NotImplemented
    set_db_stats_kwargs = NotImplemented
    func = NotImplemented
    mock_func = NotImplemented
    mock_func_return_value = NotImplemented
    mock_return_value = NotImplemented
    parse_mock_return_value = NotImplemented

    @staticmethod
    def get_histogram_response(**kwargs):
        return

    @mock.patch("core.database.get_stats")
    def test_stats_already_in_db(self, db_stats_mock):
        db_stats_mock.return_value = {"foo": 1, **self.set_db_stats_kwargs}

        with mock.patch(self.mock_func) as func_mock:
            func_mock.return_value = self.mock_return_value
            results = getattr(new_cases, self.func)()

        func_mock.assert_called_once_with(json=True)
        db_stats_mock.assert_called_once_with(**self.db_stats_kwargs)
        assert results is None

    @mock.patch("core.database.set_stats")
    @mock.patch("core.database.get_stats")
    @mock.patch("core.utils.parse_diff")
    @mock.patch("scrapers.formatters.parse_global")
    def test_set_stats_if_not_in_db(
        self, parse_mock, diff_mock, get_db_stats_mock, set_db_stats_mock,
    ):
        diff_mock.return_value = "diff_mock"
        get_db_stats_mock.return_value = {"foo": 1}
        parse_mock.return_value = "parse_global_result"

        with mock.patch(self.mock_func) as func_mock:
            func_mock.return_value = self.mock_func_return_value
            results = getattr(new_cases, self.func)()

        func_mock.assert_called_once_with(json=True)
        get_db_stats_mock.assert_called_once_with(**self.db_stats_kwargs)
        set_db_stats_mock.assert_called_once_with(
            {"foo": 1, "bar": 2, **self.set_db_stats_kwargs},
            **self.db_stats_kwargs,
        )
        parse_mock.assert_called_once_with(**self.parse_mock_return_value)
        assert results == "parse_global_result"


class TestGetHistogram(BaseNewCasesMixin):
    db_stats_kwargs = {}
    set_db_stats_kwargs = {"vindecati": 3, "decedati": 4, "confirmati": 5}
    func = "get_quick_stats"
    mock_func = "scrapers.histogram"
    mock_func_return_value = {
        "quickStats": {
            "totals": {
                "foo": 1,
                "bar": 2,
                "cured": 3,
                "deaths": 4,
                "confirmed": 5,
            }
        }
    }
    mock_return_value = {
        "quickStats": {
            "totals": {"foo": 1, "cured": 3, "deaths": 4, "confirmed": 5}
        }
    }
    parse_mock_return_value = {
        "title": "🔴 Cazuri noi",
        "stats": "diff_mock",
        "items": {},
    }


class TestGetLatestNews(BaseNewCasesMixin):
    db_stats_kwargs = {"slug": "stiri-oficiale-slug"}
    set_db_stats_kwargs = {}
    func = "get_latest_news"
    mock_func = "scrapers.latest_article"
    mock_func_return_value = {
        "bar": 2,
        "descriere": "description",
        "foo": 1,
        "titlu": "titlu foo",
        "url": "http://foo.url",
    }
    mock_return_value = {"foo": 1}
    parse_mock_return_value = {
        "emoji": "❗",
        "items": {"description": ["http://foo.url"]},
        "stats": {"bar": 2, "foo": 1},
        "title": "🔵 titlu foo",
    }


class TestCheckNewCases:
    view_name = "new_cases_views.check_new_cases"

    @pytest.mark.parametrize("method", ["get", "put", "delete", "head"])
    def test_methods_not_allowed(self, client, method):
        method = getattr(client, method)
        response = method(url_for(self.view_name, what="foo", token="bar"))
        assert response.status_code == 405

    @mock.patch("core.database.get_collection")
    def test_with_bad_token(self, collection, client):
        collection.return_value.find_one.return_value = None
        response = client.post(url_for(self.view_name, what="wh", token="tok"))
        collection.assert_called_with("oicd_auth")
        collection().find_one.assert_called_with({"bearer": "tok"})
        assert response.status_code == 403

    @mock.patch("core.database.get_collection")
    def test_with_bad_what_param(self, collection, client):
        collection.return_value.find_one.return_value = True
        response = client.post(url_for(self.view_name, what="wh", token="tok"))
        collection.assert_called_with("oicd_auth")
        collection().find_one.assert_called_with({"bearer": "tok"})
        assert response.status_code == 404

    @pytest.mark.parametrize("func", new_cases.FUNCS)
    @mock.patch("core.database.get_collection")
    def test_with_no_changes(self, collection, func, client):
        collection.return_value.find_one.return_value = True

        with mock.patch(f"core.views.new_cases.FUNCS") as funcs_mock:
            funcs_mock.__contains__.return_value = True
            funcs_mock.__getitem__.return_value.return_value = None
            response = client.post(
                url_for(self.view_name, what=func, token="tok")
            )
        collection.assert_called_with("oicd_auth")
        collection().find_one.assert_called_with({"bearer": "tok"})
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "No changes"

    @pytest.mark.parametrize("func", new_cases.FUNCS)
    @mock.patch("telegram.Bot")
    @mock.patch("core.database.get_collection")
    def test_with_changes(self, collection, bot, func, client):
        bot.return_value.sendMessage.return_value.to_json.return_value = "res"
        collection.return_value.find_one.return_value = True

        with mock.patch(f"core.views.new_cases.FUNCS") as funcs_mock:
            funcs_mock.__contains__.return_value = True
            response = client.post(
                url_for(self.view_name, what=func, token="tok")
            )
        collection.assert_called_with("oicd_auth")
        collection().find_one.assert_called_with({"bearer": "tok"})
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "res"
