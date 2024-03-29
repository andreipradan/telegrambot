import os
from unittest import mock

import pytest
import telegram
from flask import url_for

from core import constants
from inlines import markups


@mock.patch("telegram.Bot", return_value="Bot_foo")
@mock.patch("telegram.Update.de_json")
class TestWebhook:
    view_name = "webhook_views.webhook"

    @pytest.mark.parametrize("method", ["get", "put", "delete", "head"])
    def test_methods_not_allowed(self, _, __, client, method):
        method = getattr(client, method)
        response = method(url_for(self.view_name))
        assert response.status_code == 405

    @pytest.mark.skip(reason="Todo: Check why flask 2 is not throwing error")
    def test_no_json_in_payload(self, _, __, client):
        with pytest.raises(ValueError) as e:
            client.post(url_for(self.view_name))
        assert e.value.args[0] == "No payload"

    @pytest.mark.parametrize("inline_func", ["end", "back", "more"])
    def test_callback_query_end(self, json_mock, _, client, inline_func):
        json_mock.return_value.callback_query.data = inline_func

        with mock.patch(f"inlines.inline.{inline_func}") as inline_mock:
            inline_mock.return_value = f"inline_{inline_func}_foo"
            response = client.post(url_for(self.view_name), json={"1": 2})

        json_mock.assert_called_once_with({"1": 2}, "Bot_foo")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == f"inline_{inline_func}_foo"

    @pytest.mark.parametrize(
        "local_data_func",
        [
            x.callback_data
            for x in markups.COVID.inline_keyboard[0]
            if x.callback_data not in ["end", "back", "more"]
        ],
    )
    @mock.patch("inlines.inline.refresh_data", return_value="refresh_data")
    def test_refresh_data(self, _, de_json, ___, client, local_data_func):
        de_json.return_value.callback_query.data = local_data_func

        with mock.patch(f"core.local_data.{local_data_func}") as local_func:
            response = client.post(url_for(self.view_name), json={"1": 2})
        de_json.assert_called_once_with({"1": 2}, "Bot_foo")
        local_func.assert_called_once_with()
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "refresh_data"

    @mock.patch("core.handlers.validate_components")
    def test_1337_status_skip_debug(self, validate, update, _, client):
        validate.return_value = "skip-debug", 1337
        update.return_value.callback_query = None
        response = client.post(url_for(self.view_name), json={"1": 2})
        validate.assert_called_once_with(mock.ANY)
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "ok"

    @mock.patch("core.utils.send_message")
    @mock.patch("core.handlers.validate_components")
    def test_1337_status_debug(self, validate, message, update, _, client):
        message.return_value = "send_foo"
        validate.return_value = "command_text_foo", 1337
        update.return_value.callback_query = None

        response = client.post(url_for(self.view_name), json={"1": 2})
        validate.assert_called_once_with(update())
        message.assert_called_with(
            "Bot_foo", text=f"command_text_foo.\nUpdate: {update().to_dict()}"
        )
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "send_foo"

    @mock.patch("core.utils.send_message", return_value="send_foo")
    @mock.patch("core.handlers.validate_components")
    def test_invalid_command(self, validate, message, update, _, client):
        validate.return_value = "command_text_foo", "foo_command"
        update.return_value.callback_query = None
        update.return_value.message.from_user.username = "foo"
        os.environ["WHITELIST"] = "foo"

        response = client.post(url_for(self.view_name), json={"1": 2})
        validate.assert_called_once_with(update())
        message.assert_called_once_with(
            "Bot_foo",
            text="command_text_foo",
            chat_id=update().message.chat.id,
        )
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "send_foo"

    @mock.patch("inlines.inline.start", return_value="inline_start_foo")
    @mock.patch("core.handlers.validate_components")
    def test_start(self, validate, start, update, _, client):
        validate.return_value = "start", "valid-command"
        update.return_value.callback_query = None
        update.return_value.message.from_user.username = "foo"
        os.environ["WHITELIST"] = "foo"
        response = client.post(url_for(self.view_name), json={"1": 2})

        start.assert_called_once_with(update())
        validate.assert_called_once_with(update())

        assert response.status_code == 200
        assert response.data.decode("utf-8") == "inline_start_foo"

    @mock.patch("core.utils.send_message")
    @mock.patch("api.views.webhook.analyze_sentiment")
    @mock.patch("core.handlers.validate_components")
    def test_message_too_long(self, validate, scrape, msg, update, _, client):
        scrape.return_value = "scrapers_foo"
        msg.side_effect = telegram.error.BadRequest("foo")
        validate.return_value = "analyze_sentiment", "valid-command"
        update.return_value.callback_query = None
        update().message.chat.type = "private"
        update().message.chat.id = constants.GOOGLE_CLOUD_WHITELIST["private"][
            0
        ]
        update.return_value.message.from_user.username = "foo"
        os.environ["WHITELIST"] = "foo"
        with pytest.raises(telegram.error.BadRequest) as e:
            client.post(url_for(self.view_name), json={"1": 2})

        assert e.value.message == "foo"

        validate.assert_called_once_with(update())
        scrape.assert_called_once_with("")
