from unittest import mock

import pytest
from flask import url_for


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
    def test_with_no_changes(self, collection, client):
        collection.return_value.find_one.return_value = True

        with mock.patch(f"api.views.new_cases.DateLaZiClient") as dlz_mock:
            dlz_mock.return_value.sync_archive.return_value = None
            response = client.post(url_for(self.view_name, token="tok"))
        collection.assert_called_with("oicd_auth")
        collection().find_one.assert_called_with({"bearer": "tok"})
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "No changes"

    @mock.patch("telegram.Bot")
    @mock.patch("core.database.get_collection")
    def test_with_changes(self, collection, bot, client, monkeypatch):
        monkeypatch.setenv("CHAT_ID", "test_chat_id")
        bot.return_value.sendMessage.return_value.to_json.return_value = "res"
        collection.return_value.find_one.return_value = True

        with mock.patch(f"api.views.new_cases.DateLaZiClient"):
            response = client.post(url_for(self.view_name, token="tok"))
        collection.assert_called_with("oicd_auth")
        collection().find_one.assert_called_with({"bearer": "tok"})
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "res"
