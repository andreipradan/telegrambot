from unittest import mock

import pytest
from flask import url_for

from core.views import new_cases
from serializers import DLZSerializer


class TestGetQuickStats:
    func = "get_quick_stats"

    @mock.patch("requests.get")
    @mock.patch("core.views.new_cases.DLZSerializer")
    @mock.patch("core.database.get_stats")
    def test_stats_already_in_db(self, db_stats_mock, serializer, get):
        serializer.return_value.data = {"foo": 1}
        db_stats_mock.return_value = {"foo": 1}
        results = getattr(new_cases, self.func)()
        get.assert_called_once_with("https://api1.datelazi.ro/api/v2/data/")
        get().raise_for_status.assert_called_once_with()
        db_stats_mock.assert_called_once_with(slug="romania-slug")
        assert results is None

    @mock.patch("core.parsers.parse_diff")
    @mock.patch("scrapers.formatters.parse_global")
    @mock.patch("core.database.get_stats")
    @mock.patch("core.views.new_cases.DLZSerializer")
    @mock.patch("requests.get")
    def test_set_stats_no_new_quick_stats(self, get, ser, db_get, par, diff):
        diff.return_value = {"diff_mock": 1}
        par.return_value = "parse_global_result"
        ser().data = {"foo": 1, "bar": 2}
        db_get.return_value = {"foo": 1}
        results = getattr(new_cases, self.func)()
        get.assert_called_once_with("https://api1.datelazi.ro/api/v2/data/")
        get().raise_for_status.assert_called_once_with()
        db_get.assert_called_once_with(slug="romania-slug")
        ser().save.assert_called_once_with()
        assert not par.called
        assert results is None

    @mock.patch("core.views.new_cases.parse_diff")
    @mock.patch("core.views.new_cases.parse_global")
    @mock.patch("core.database.get_stats")
    @mock.patch("core.views.new_cases.DLZSerializer")
    @mock.patch("requests.get")
    def test_set_stats_if_not_in_db(self, get, ser, db_get, par, diff):
        get.return_value.json.return_value = {
            "currentDayStats": {
                "numberInfected": 2,
                "numberCured": 3,
                "numberDeceased": 4,
                "Actualizat la": 5,
                "parsedOnString": "foo",
                "parsedOn": "foo",
            },
            "historicalData": {},
        }
        diff.return_value = {"diff_mock": 1}
        par.return_value = "parse_global_result"
        ser().data = {"foo": 1, "bar": 2}
        ser.deserialize_fields = DLZSerializer.deserialize_fields
        ser.mapped_fields = DLZSerializer.mapped_fields
        db_get.return_value = {"foo": 1}
        results = new_cases.get_quick_stats()
        get.assert_called_once_with("https://api1.datelazi.ro/api/v2/data/")
        get().raise_for_status.assert_called_once_with()
        db_get.assert_called_once_with(slug="romania-slug")
        ser().save.assert_called_once_with()
        par.assert_called_once_with(
            title="🔴 Cazuri noi",
            stats={"diff_mock": 1, "Actualizat la": ser().deserialize().pop()},
            items={},
        )
        assert results == "parse_global_result"


class TestGetLatestNews:
    @staticmethod
    def get_histogram_response(**kwargs):
        return

    @mock.patch("core.database.get_stats")
    def test_stats_already_in_db(self, db_stats_mock):
        db_stats_mock.return_value = {"foo": 1}

        with mock.patch(
            "core.views.new_cases.StiriOficialeClient"
        ) as func_mock:
            func_mock.return_value.sync.return_value = None
            results = new_cases.get_latest_news()

        func_mock.assert_called_once_with()
        assert results is None

    @mock.patch("core.database.set_stats")
    @mock.patch("core.database.get_stats")
    @mock.patch("core.parsers.parse_diff")
    @mock.patch("core.views.new_cases.parse_global")
    def test_set_stats_if_not_in_db(
        self, parse_mock, diff_mock, get_db_stats_mock, set_db_stats_mock,
    ):
        diff_mock.return_value = "diff_mock"
        get_db_stats_mock.return_value = {"foo": 1}
        parse_mock.return_value = "parse_global_result"

        with mock.patch(
            "core.views.new_cases.StiriOficialeClient"
        ) as func_mock:
            func_mock.return_value.sync.return_value = {
                "bar": 2,
                "descriere": "description",
                "foo": 1,
                "titlu": "titlu foo",
                "url": "http://foo.url",
            }
            results = new_cases.get_latest_news()

        func_mock.assert_called_once_with()
        parse_mock.assert_called_once_with(
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
    def test_with_changes(self, collection, bot, func, client, monkeypatch):
        monkeypatch.setenv("CHAT_ID", "test_chat_id")
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
