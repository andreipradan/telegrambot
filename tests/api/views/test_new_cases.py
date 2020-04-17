from unittest import mock

import pytest
from flask import url_for

from api.views import new_cases


class TestGetLatestNews:
    @staticmethod
    def get_histogram_response(**kwargs):
        return

    @mock.patch("core.database.get_stats")
    def test_stats_already_in_db(self, db_stats_mock):
        db_stats_mock.return_value = {"foo": 1}

        with mock.patch("api.views.new_cases.StiriOficialeClient") as fm:
            fm.return_value.sync.return_value = None
            results = new_cases.get_latest_news()

        fm.assert_called_once_with()
        assert results is None

    @mock.patch("core.database.set_stats")
    @mock.patch("core.database.get_stats")
    @mock.patch("core.parsers.parse_diff")
    @mock.patch("api.views.new_cases.parse_global")
    def test_set_stats_if_not_in_db(
        self, parser, diff_mock, db_stats, _,
    ):
        diff_mock.return_value = "diff_mock"
        db_stats.return_value = {"foo": 1}
        parser.return_value = "parse_global_result"

        with mock.patch("api.views.new_cases.StiriOficialeClient") as fm:
            fm.return_value.sync.return_value = {
                "bar": 2,
                "descriere": "description",
                "foo": 1,
                "titlu": "titlu foo",
                "url": "http://foo.url",
            }
            results = new_cases.get_latest_news()

        fm.assert_called_once_with()
        parser.assert_called_once_with(
            emoji="❗",
            items={"description": ["http://foo.url"]},
            stats={"bar": 2, "foo": 1},
            title="🔵 titlu foo",
        )
        assert results == "parse_global_result"


class TestCheckNewCases:
    view_name = "new_cases_views.check_new_cases"

    @property
    def url(self):
        return url_for(self.view_name, what="foo", token="bar")

    @pytest.mark.parametrize("method", ["get", "put", "delete", "head"])
    def test_methods_not_allowed(self, client, method):
        method = getattr(client, method)
        response = method(self.url)
        assert response.status_code == 405

    # @pytest.mark.skip(reason="not yet")
    # def test_with_no_token(self, client):
    #     assert client.post(self.url).status_code == 403

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

        with mock.patch(f"api.views.new_cases.FUNCS") as funcs_mock:
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
    def test_with_changes(self, collection, bot, func, client, monkeypatch):
        monkeypatch.setenv("CHAT_ID", "test_chat_id")
        bot.return_value.sendMessage.return_value.to_json.return_value = "res"
        collection.return_value.find_one.return_value = True

        with mock.patch(f"api.views.new_cases.FUNCS") as funcs_mock:
            funcs_mock.__contains__.return_value = True
            response = client.post(
                url_for(self.view_name, what=func, token="tok")
            )
        collection.assert_called_with("oicd_auth")
        collection().find_one.assert_called_with({"bearer": "tok"})
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "res"
