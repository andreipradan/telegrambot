from unittest.mock import MagicMock

import pytest

from core import utils, constants


class TestParseDiff:
    @pytest.mark.parametrize("data", [{"foo": 1}, "bar", None, [], {}])
    def test_no_old_version(self, data):
        assert utils.parse_diff(data, None) == data

    def test_same_values(self):
        data = {"abc": 1, "cde": 2}
        assert utils.parse_diff(data, data) == data

    def test_different_keys(self):
        data = {"abc": 1, "cde": 2}
        old_values = {"fgh": 123, "ijk": 456}
        assert utils.parse_diff(data, old_values) == data

    @pytest.mark.parametrize(
        ("data", "old_data", "results"),
        [
            (
                {"abc": 123, "def": 456},
                {"abc": 125, "def": 449},
                {"abc": "123 (-2)", "def": "456 (+7)"},
            ),
            (
                {"abc": 123, "def": 456, "jkl": 678},
                {"abc": 123, "def": 451},
                {"abc": 123, "def": "456 (+5)", "jkl": 678},
            ),
        ],
    )
    def test_different_values(self, data, old_data, results):
        assert utils.parse_diff(data, old_data) == results


@pytest.mark.parametrize(
    ("user", "result"),
    [
        (MagicMock(first_name="foo", last_name="bar"), "foo bar"),
        (MagicMock(first_name=None, last_name="bar"), "bar"),
        (MagicMock(first_name=None, last_name=None, username="cux"), "cux"),
    ],
)
def test_parse_name(user, result):
    assert utils.parse_name(user) == result


def test_send_message_without_chat_id():
    bot = MagicMock()
    bot.send_message.return_value.to_json.return_value = "sent..."
    assert utils.send_message(bot, text="hey foo!") == "sent..."
    bot.send_message.assert_called_once_with(
        chat_id=constants.DEBUG_CHAT_ID,
        text="hey foo!",
        disable_notification=True,
    )
    bot.send_message.return_value.to_json.assert_called_once_with()


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
    assert utils.parse_sentiment(data) == result
