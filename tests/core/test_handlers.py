from unittest import mock
from unittest.mock import MagicMock

import pytest

from core import constants
from core.handlers import validate_components


class TestValidateComponents:
    missing_error = "Missing message, chat or chat ID. Update: {}"

    def test_callback_query(self):
        update = MagicMock()
        assert validate_components(update) == (
            "inline",
            update.callback_query.data,
        )

    def test_edited_message(self):
        update = MagicMock(callback_query=None, message=None)
        assert validate_components(update) == (f"skip-debug", 1337)

    def test_channel_post(self):
        update = MagicMock(
            callback_query=None, message=None, edited_message=None
        )
        assert validate_components(update) == ("skip-debug", 1337)

    def test_left_chat_member(self):
        update = MagicMock(callback_query=None)
        update.message.text = None
        assert validate_components(update) == ("😢", 400)

    def test_new_chat_title(self):
        update = MagicMock(
            callback_query=None,
            message=MagicMock(text=None, left_chat_member=None),
        )
        assert validate_components(update) == ("🎉", 400)

    def test_new_chat_members(self):
        update = MagicMock(
            callback_query=None,
            message=MagicMock(
                text=None,
                left_chat_member=None,
                new_chat_title=None,
                new_chat_members=["foo", "bar"],
            ),
        )
        with mock.patch("core.handlers.parse_name") as parse_mock:
            parse_mock.side_effect = update.message.new_chat_members
            assert validate_components(update) == ("Welcome foo, bar!", 400)

    def test_photo(self):
        update = MagicMock(
            callback_query=None,
            message=MagicMock(
                text=None,
                left_chat_member=None,
                new_chat_title=None,
                new_chat_members=None,
            ),
        )
        assert validate_components(update) == ("skip-debug", 1337)

    def test_no_message_text_unhandled(self):
        update = MagicMock(
            callback_query=None,
            message=MagicMock(
                text=None,
                left_chat_member=None,
                new_chat_title=None,
                new_chat_members=None,
                new_chat_photo=None,
                group_chat_created=None,
                supergroup_chat_created=None,
                channel_chat_created=None,
                pinned_message=None,
                photo=None,
                document=None,
                animation=None,
            ),
        )
        with pytest.raises(ValueError) as e:
            validate_components(update)

        assert (
            e.value.args[0] == f"No message text. Update: {update.to_dict()}"
        )

    def test_reply_to_message(self):
        update = MagicMock(
            callback_query=None, message=MagicMock(text="reply_foo")
        )
        assert validate_components(update) == ("skip-debug", 1337)

    def test_invalid_command(self):
        message = MagicMock(reply_to_message=None, text="reply_foo")
        update = MagicMock(callback_query=None, message=message)
        assert validate_components(update) == (
            f'Invalid command: "reply_foo".\nCommands start with "/".',
            "send-message",
        )

    def test_unknown_command_not_whitelisted(self):
        message = MagicMock(reply_to_message=None, text="/command_foo 123 4")
        update = MagicMock(callback_query=None, message=message)
        update.message.chat.type = "private"
        assert validate_components(update) == (
            f'Unknown command: "command_foo".\n'
            f"Available commands: \n• /start",
            400,
        )

    def test_unknown_command_whitelisted(self):
        message = MagicMock(reply_to_message=None, text="/command_foo 123 4")
        update = MagicMock(callback_query=None, message=message)
        update.message.chat.type = "private"
        update.message.chat_id = constants.GOOGLE_CLOUD_WHITELIST["private"][0]
        assert validate_components(update) == (
            'Unknown command: "command_foo".\n'
            "Available commands: \n• /analyze_sentiment\n• "
            "/start\n• /translate\n• /games\n• /randomize",
            400,
        )

    @pytest.mark.parametrize("command", constants.ALLOWED_COMMANDS)
    def test_return_actual_command(self, command):
        message = MagicMock(reply_to_message=None, text=f"/{command}")
        update = MagicMock(callback_query=None, message=message)
        assert validate_components(update) == (command, "valid-command")
