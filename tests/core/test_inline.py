from unittest import mock
from unittest.mock import MagicMock

import pytest
import telegram

from core import inline


class InlineMixin:
    edit_kwargs = NotImplemented
    func = NotImplemented
    kwargs = NotImplemented
    text = NotImplemented

    @pytest.mark.parametrize("with_error", [True, False])
    def test_method(self, with_error):
        if with_error:
            edit = MagicMock(
                side_effect=telegram.error.BadRequest("foo_error")
            )
            result = "foo_error"
        else:
            json = MagicMock(return_value="edited")
            edit = MagicMock(return_value=MagicMock(to_json=json))
            result = "edited"

        query = MagicMock(bot=MagicMock(edit_message_text=edit))
        update = MagicMock(callback_query=query)
        assert getattr(inline, self.func)(update, **self.kwargs) == result

        if self.kwargs:
            self.edit_kwargs["reply_markup"] = query.message.reply_markup
        update.callback_query.bot.edit_message_text.assert_called_once_with(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=self.text,
            **self.edit_kwargs
        )


class TestEnd(InlineMixin):
    func = "end"
    edit_kwargs = {}
    kwargs = {}
    text = "See you next time!"


class TestMore(InlineMixin):
    func = "more"
    edit_kwargs = {"reply_markup": inline.MORE_MARKUP}
    kwargs = {}
    text = "Choose an option"


class TestRefreshData(InlineMixin):
    func = "refresh_data"
    edit_kwargs = {"disable_web_page_preview": True, "parse_mode": "Markdown"}
    kwargs = {"command": "foo"}
    text = "foo\n" + "\t" * 50


class TestBack(InlineMixin):
    func = "back"
    edit_kwargs = {"reply_markup": inline.START_MARKUP}
    kwargs = {}
    text = "Hello! Choose an option"


@mock.patch("core.inline.logger.info")
def test_start(logger):
    update = MagicMock()
    update.message.from_user.first_name = "first_foo"
    assert (
        inline.start(update)
        == update.message.reply_text.return_value.to_json.return_value
    )
    logger.assert_called_once_with(
        "User %s started the conversation.", "first_foo"
    )
    update.message.reply_text.assert_called_once_with(
        "Hello! Choose an option", reply_markup=inline.START_MARKUP
    )
