import os
from unittest import mock
from unittest.mock import MagicMock

import pytest
import telegram
from telegram.error import Unauthorized

from core.parsers import parse_sentiment
from core.utils import send_message


def test_send_message_without_chat_id():
    bot = MagicMock()
    bot.send_message.return_value.to_json.return_value = "sent..."
    assert send_message(bot, text="hey foo!") == "sent..."
    bot.send_message.assert_called_once_with(
        chat_id=os.getenv("DEBUG_CHAT_ID"),
        text="hey foo!",
        disable_notification=True,
        parse_mode="Markdown",
    )
    bot.send_message.return_value.to_json.assert_called_once_with()


def test_send_message_unauthorized():
    bot = MagicMock()
    bot.send_message.side_effect = Unauthorized("err")
    assert send_message(bot, text="hey foo!") == "err"


def test_send_message_bad_request():
    bot = MagicMock()
    second_call = MagicMock()
    second_call.to_json.return_value = "foo"
    bot.send_message.side_effect = [
        telegram.error.BadRequest("err"),
        second_call,
    ]
    assert send_message(bot, text="hey foo!") == "foo"


@pytest.mark.parametrize(
    ("data", "result"),
    [
        ("foo_string", "foo_string"),
        ({"Overall score": -1}, "Why so negative?"),
        ({"Overall score": 2}, "Nice to see you positive like that!"),
        (
            {"Overall score": 0},
            "You nailed it! You don't see everyday a neutral attitude.",
        ),
    ],
)
def test_parse_sentiment(data, result):
    assert parse_sentiment(data) == result
