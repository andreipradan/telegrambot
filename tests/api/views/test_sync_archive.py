from unittest import mock

import pytest
from flask import url_for


class TestSyncArchive:
    view_name = "new_cases_views.sync_archive"

    @property
    def url(self):
        return url_for(self.view_name, what="foo", token="bar")

    @pytest.mark.parametrize("method", ["get", "put", "delete", "head"])
    def test_methods_not_allowed(self, client, method):
        method = getattr(client, method)
        response = method(self.url)
        assert response.status_code == 405

    def test_with_no_changes(self, client, monkeypatch):
        monkeypatch.setenv("DISABLE_HEADER_AUTH", "True")
        with mock.patch(f"api.views.new_cases.DateLaZiClient") as dlz_mock:
            dlz_mock.return_value.sync_archive.return_value = None
            response = client.post(url_for(self.view_name, token="tok"))
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "No changes"

    @mock.patch("telegram.Bot")
    def test_with_changes(self, bot, client, monkeypatch):
        monkeypatch.setenv("CHAT_ID", "test_chat_id")
        monkeypatch.setenv("DISABLE_HEADER_AUTH", "True")
        bot.return_value.sendMessage.return_value.to_json.return_value = "res"

        with mock.patch(f"api.views.new_cases.DateLaZiClient"):
            response = client.post(url_for(self.view_name, token="tok"))
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "res"
