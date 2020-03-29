from unittest import mock

import pytest
from flask import url_for

from core import constants


def test_command_list_data(client):
    response = client.get(url_for("commands_views.command_list"))
    assert response.status_code == 200
    assert response.json == {
        "count": len(constants.COMMANDS_FOR_VIEWS),
        "data": [
            url_for(
                "commands_views.command", command_name=command, _external=True
            )
            for command in constants.COMMANDS_FOR_VIEWS
        ],
        "errors": [],
        "links": {"home": url_for("site_map")},
    }


class TestCommandView:
    view_name = "commands_views.command"

    @staticmethod
    def get_response_data(**kwargs):
        return {
            "count": 0,
            "data": {},
            "links": {"home": url_for("commands_views.command_list")},
            "errors": [],
            **kwargs,
        }

    def test_not_command_for_views(self, client):
        response = client.get(url_for(self.view_name, command_name="foo"))
        assert response.status_code == 400
        assert response.json == self.get_response_data(
            errors=[
                "Unknown command: 'foo'. Navigate 'home' (from 'links') "
                "to see the list of commands."
            ]
        )

    @pytest.mark.parametrize("command", constants.COMMANDS_WITH_TEXT)
    def test_text_commands_no_text_provided(self, client, command):
        resp = client.get(url_for(self.view_name, command_name=command))
        assert resp.status_code == 400
        assert resp.json == self.get_response_data(
            errors=[
                f"This command requires a text URL param. "
                f"e.g. http://example.com/commands/{command}/?text=hello"
            ]
        )

    @pytest.mark.parametrize("command", constants.COMMANDS_WITH_TEXT)
    def test_valid_commands_with_text(self, client, command):
        with mock.patch(f"scrapers.{command}") as scraper_mock:
            scraper_mock.return_value = "foo"
            resp = client.get(
                url_for(self.view_name, command_name=command) + "?text=foo"
            )
        scraper_mock.assert_called_with(json=True, text="foo")
        assert resp.status_code == 200
        assert resp.json == self.get_response_data(count=1, data="foo")

    @pytest.mark.parametrize(
        "command",
        set(constants.COMMANDS_FOR_VIEWS) - set(constants.COMMANDS_WITH_TEXT),
    )
    def test_valid_commands_without_text(self, client, command):
        with mock.patch(f"scrapers.{command}") as scraper_mock:
            scraper_mock.return_value = "foo"
            resp = client.get(url_for(self.view_name, command_name=command))
        scraper_mock.assert_called_with(json=True)
        assert resp.status_code == 200
        assert resp.json == self.get_response_data(count=1, data="foo")
