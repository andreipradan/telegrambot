from unittest import mock

import pytest
from flask import url_for


@mock.patch("telegram.Bot", return_value="Bot_foo")
class TestWebhook:
    view_name = "webhook_views.webhook"

    @pytest.mark.parametrize("method", ["get", "put", "delete", "head"])
    def test_with_not_allowed_methods(self, _, client, method):
        method = getattr(client, method)
        response = method(url_for(self.view_name))
        assert response.status_code == 405

    def test_no_json_in_payload(self, _, client):
        with pytest.raises(ValueError) as e:
            client.post(url_for(self.view_name))
        assert e.value.args[0] == "No payload"

    @pytest.mark.parametrize("inline_func", ["end", "back", "more"])
    @mock.patch("telegram.Update.de_json")
    def test_callback_query_end(self, json_mock, _, client, inline_func):
        json_mock.return_value.callback_query.data = inline_func

        with mock.patch(f"core.inline.{inline_func}") as inline_mock:
            inline_mock.return_value = f"inline_{inline_func}_foo"
            response = client.post(url_for(self.view_name), json={"1": 2})

        json_mock.assert_called_once_with({"1": 2}, "Bot_foo")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == f"inline_{inline_func}_foo"

    @mock.patch("scrapers.date_la_zi")
    @mock.patch("core.inline.refresh_data", return_value="refresh_data")
    @mock.patch("telegram.Update.de_json")
    def test_refresh_data(self, de_json, _, __, ___, client):
        de_json.return_value.callback_query.data = "date_la_zi"

        response = client.post(url_for(self.view_name), json={"1": 2})
        de_json.assert_called_once_with({"1": 2}, "Bot_foo")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "refresh_data"

    @mock.patch("telegram.Update.de_json")
    @mock.patch("core.handlers.validate_components")
    def test_1337_status_skip_debug(self, validate, update, _, client):
        validate.return_value = "skip-debug", 1337
        update.return_value.callback_query = None
        response = client.post(url_for(self.view_name), json={"1": 2})
        validate.assert_called_once_with(mock.ANY)
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "ok"

    @mock.patch("core.utils.send_message")
    @mock.patch("telegram.Update.de_json")
    @mock.patch("core.handlers.validate_components")
    def test_1337_status_debug(self, validate, update, message, _, client):
        message.return_value = "send_foo"
        validate.return_value = "command_text_foo", 1337
        update.return_value.callback_query = None

        response = client.post(url_for(self.view_name), json={"1": 2})
        validate.assert_called_once_with(mock.ANY)
        message.assert_called_with(
            "Bot_foo", text=f"command_text_foo.\nUpdate: {update().to_dict()}"
        )
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "send_foo"
