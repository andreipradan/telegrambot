from unittest import mock
from unittest.mock import MagicMock

import pytest

from core import constants
from core.handlers import validate_components


class TestValidateComponents:
    missing_error = "Missing message, chat or chat ID. Update: {}"

    def test_edited_message(self):
        update = MagicMock(message=None)
        assert validate_components(update) == (f"✂️", 1337)

    def test_channel_post(self):
        update = MagicMock(message=None, edited_message=None)
        assert validate_components(update) == ("skip-debug", 1337)

    def test_missing_message_raises_value_error(self):
        update = MagicMock(edited_message=None, channel_post=None)
        update.message = None
        with pytest.raises(ValueError) as e:
            validate_components(update)

        assert e.value.args[0] == self.missing_error.format(update.to_dict())

    def test_missing_chat_raises_value_error(self):
        update = MagicMock(edited_message=None, channel_post=None)
        update.message.chat = None
        with pytest.raises(ValueError) as e:
            validate_components(update)
        assert e.value.args[0] == self.missing_error.format(update.to_dict())

    def test_missing_chat_id_raises_value_error(self):
        update = MagicMock(edited_message=None, channel_post=None)
        update.message.chat.id = None
        with pytest.raises(ValueError) as e:
            validate_components(update)
        assert e.value.args[0] == self.missing_error.format(update.to_dict())

    def test_left_chat_member(self):
        update = MagicMock()
        update.message.text = None
        assert validate_components(update) == ("😢", 400)

    def test_new_chat_title(self):
        update = MagicMock(message=MagicMock(text=None, left_chat_member=None))
        assert validate_components(update) == ("🎉", 400)

    def test_new_chat_members(self):
        update = MagicMock(
            message=MagicMock(
                text=None,
                left_chat_member=None,
                new_chat_title=None,
                new_chat_members=["foo", "bar"],
            )
        )
        with mock.patch("core.handlers.parse_name") as parse_mock:
            parse_mock.side_effect = update.message.new_chat_members
            assert validate_components(update) == ("Welcome foo, bar!", 400)

    def test_photo(self):
        update = MagicMock(
            message=MagicMock(
                text=None,
                left_chat_member=None,
                new_chat_title=None,
                new_chat_members=None,
            )
        )
        assert validate_components(update) == ("skip-debug", 1337)

    def test_no_message_text_unhandled(self):
        update = MagicMock(
            message=MagicMock(
                text=None,
                left_chat_member=None,
                new_chat_title=None,
                new_chat_members=None,
                photo=None,
            )
        )
        with pytest.raises(ValueError) as e:
            validate_components(update)

        assert (
            e.value.args[0] == f"No message text. Update: {update.to_dict()}"
        )

    def test_reply_to_message(self):
        update = MagicMock(message=MagicMock(text="reply_foo"))
        assert validate_components(update) == ("reply_foo", "reply_to_message")

    def test_invalid_command(self):
        message = MagicMock(reply_to_message=None, text="reply_foo")
        update = MagicMock(message=message)
        assert validate_components(update) == (
            f'Invalid command: "reply_foo".\nCommands start with "/".',
            "send-message",
        )

    def test_unknown_command_not_whitelisted(self):
        message = MagicMock(reply_to_message=None, text="/command_foo 123 4")
        update = MagicMock(message=message)
        update.message.chat.type = "private"
        assert validate_components(update) == (
            f'Unknown command: "command_foo".\n'
            f"Available commands: \n• /start",
            400,
        )

    def test_unknown_command_whitelisted(self):
        message = MagicMock(reply_to_message=None, text="/command_foo 123 4")
        update = MagicMock(message=message)
        update.message.chat.type = "private"
        update.message.chat_id = constants.GOOGLE_CLOUD_WHITELIST["private"][0]
        assert validate_components(update) == (
            f'Unknown command: "command_foo".\n'
            f"Available commands: \n• /analyze_sentiment\n• /start\n• /translate",
            400,
        )

    @pytest.mark.parametrize("command", constants.ALLOWED_COMMANDS)
    def test_return_actual_command(self, command):
        message = MagicMock(reply_to_message=None, text=f"/{command}")
        update = MagicMock(message=message)
        assert validate_components(update) == (command, "valid-command")
