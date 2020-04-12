from unittest import mock

from core.local_data import (
    prepare_items,
    local_quick_stats,
    local_latest_article,
    datelazi,
    local_global_stats,
)


def test_prepare_items():
    assert prepare_items(
        "foo_title", [{"foo_title": 1, "bar": 1}, {"foo_title": 2}]
    ) == {1: {"bar": 1}, 2: {}}


@mock.patch("core.local_data.DLZSerializer")
@mock.patch("core.database.get_stats")
@mock.patch("core.local_data.formatters.parse_global")
def test_local_quick_stats(parse_mock, _, ser):
    parse_mock.return_value = "foo"
    assert local_quick_stats() == "foo"
    parse_mock.assert_called_once_with(
        items={}, stats=ser.deserialize(), title="🔴 Cazuri noi"
    )


@mock.patch("core.database.get_stats")
@mock.patch("core.local_data.formatters.parse_global")
def test_local_latest_article(parse_mock, *_):
    parse_mock.return_value = "foo"
    assert local_latest_article() == "foo"
    assert parse_mock.called


def test_datelazi():
    assert datelazi() == "https://datelazi.ro"


@mock.patch("core.database.get_many")
@mock.patch("core.database.get_stats")
@mock.patch("core.local_data.formatters.parse_global")
def test_local_global_stats(parse_mock, *_):
    parse_mock.return_value = "foo"
    assert local_global_stats() == "foo"
