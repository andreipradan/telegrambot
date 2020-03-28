from unittest import mock

import pytest
from flask import url_for


class TestWebhook:
    view_name = "webhook_views.webhook"

    @pytest.mark.parametrize("method", ["get", "put", "delete", "head"])
    def test_with_not_allowed_methods(self, test_client, method):
        method = getattr(test_client, method)
        response = method(url_for(self.view_name))
        assert response.status_code == 405

    def test_no_json_in_payload(self, test_client):
        with pytest.raises(ValueError) as e:
            test_client.post(url_for(self.view_name))
        assert e.value.args[0] == "No payload"

    @pytest.mark.parametrize("inline_method", ["end", "back", "more"])
    @mock.patch("telegram.Update.de_json")
    @mock.patch("telegram.Bot", return_value="Bot_foo")
    def test_callback_query_end(
        self, _, json_mock, test_client, inline_method
    ):
        update_mock = mock.MagicMock()
        update_mock.callback_query.data = inline_method
        json_mock.return_value = update_mock

        with mock.patch(f"core.inline.{inline_method}") as inline_mock:
            inline_mock.return_value = f"inline_{inline_method}_foo"
            response = test_client.post(url_for(self.view_name), json={"1": 2})

        json_mock.assert_called_once_with({"1": 2}, "Bot_foo")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == f"inline_{inline_method}_foo"

    @mock.patch("scrapers.date_la_zi")
    @mock.patch("core.inline.refresh_data", return_value="refresh_data")
    @mock.patch("telegram.Update.de_json")
    @mock.patch("telegram.Bot", return_value="Bot_foo")
    def test_refresh_data(self, _, json_mock, __, ___, test_client):
        update_mock = mock.MagicMock()
        update_mock.callback_query.data = "date_la_zi"
        json_mock.return_value = update_mock

        response = test_client.post(url_for(self.view_name), json={"1": 2})
        json_mock.assert_called_once_with({"1": 2}, "Bot_foo")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "refresh_data"
