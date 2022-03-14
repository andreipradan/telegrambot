from unittest import mock

from core import local_data


def test_prepare_items():
    assert local_data.prepare_items(
        "foo_title", [{"foo_title": 1, "bar": 1}, {"foo_title": 2}]
    ) == {1: {"bar": 1}, 2: {}}


@mock.patch("core.database.get_stats", return_value=None)
class NoStatsMxin:
    func = NotImplemented
    message = NotImplemented
    get_kwargs = NotImplemented

    def test_local_quick_stats_with_no_stats(self, get_mock):
        assert getattr(local_data, self.func)() == self.message
        get_mock.assert_called_once_with(**self.get_kwargs)


class TestLocalQuickStats(NoStatsMxin):
    func = "local_quick_stats"
    message = "Nu sunt statistici salvate pentru ziua de azi"
    get_kwargs = {"slug": "romania-slug"}

    @mock.patch("core.database.get_stats")
    @mock.patch("core.local_data.DLZSerializer")
    @mock.patch("core.local_data.formatters.parse_global")
    def test_local_quick_stats(self, parse_mock, ser, get_mock):
        parse_mock.return_value = "foo"
        assert local_data.local_quick_stats() == "foo"
        get_mock.assert_called_once_with(slug="romania-slug")
        parse_mock.assert_called_once_with(
            items={}, stats=ser.deserialize(), title="🔴 Cazuri noi"
        )


class TestLocalLatestArticle(NoStatsMxin):
    func = "local_latest_article"
    message = "Nu sunt stiri salvate pentru ziua de azi"
    get_kwargs = {"slug": "stiri-oficiale-slug"}

    @mock.patch("core.database.get_stats")
    @mock.patch("core.local_data.formatters.parse_global")
    def test_local_latest_article(self, parse_mock, get_mock):
        parse_mock.return_value = "foo"
        assert local_data.local_latest_article() == "foo"
        get_mock.assert_called_once_with(slug="stiri-oficiale-slug")
        parse_mock.assert_called_once_with(
            emoji="❗",
            items={get_mock().pop(): [get_mock().pop()]},
            stats=get_mock(),
            title=f"🔵 {get_mock().pop()}",
        )


def test_datelazi():
    assert local_data.datelazi() == "https://telegrambot.pradan.dev/"


class TestLocalGlobalStats(NoStatsMxin):
    func = "local_global_stats"
    message = "Nu sunt statistici globale pentru ziua de azi"
    get_kwargs = {"slug": "global-slug", "collection": "global-collection"}

    @mock.patch("core.database.get_stats")
    @mock.patch("core.database.get_many")
    @mock.patch("core.local_data.formatters.parse_global")
    def test_local_global_stats(self, parse_mock, get_many_mock, get_mock):
        get_many_mock.return_value = [{"_id": 1, "country": "foo_country"}]
        parse_mock.return_value = "foo"
        assert local_data.local_global_stats() == "foo"
        get_mock.assert_called_once_with(
            collection="global-collection", slug="global-slug"
        )
        parse_mock.assert_called_once_with(
            footer=f"\n`{get_mock().pop()}`\n[Source: worldometers.info](https://worldometers.info/)",
            items={"foo_country": {}},
            stats=get_mock(),
            title="🌎 Global Stats",
            emoji="🦠",
        )


class TestLocalCounties(NoStatsMxin):
    func = "local_counties"
    message = "Nu sunt date despre județe pentru ziua de azi"
    get_kwargs = {"slug": "romania-slug"}

    @mock.patch("core.database.get_stats")
    @mock.patch("core.local_data.DLZArchiveSerializer")
    @mock.patch("core.local_data.formatters.parse_global")
    def test_with_stats(self, parse_mock, ser, get_mock):
        ser.deserialize.return_value = {
            "Judete": {"AB": 1},
            "Data": "la",
        }
        parse_mock.return_value = "foo"
        assert local_data.local_counties() == "foo"
        get_mock.assert_called_once_with(slug="romania-slug")
        parse_mock.assert_called_once_with(
            emoji="🦠",
            footer="\n`Actualizat la: la`",
            items=["\nRestul județelor"] + [""] * 15,
            stats=["🦠 `AB: 1`"],
            title="🇷🇴Top cazuri confirmate",
        )


class TestLocalAge(NoStatsMxin):
    func = "local_age"
    message = "Nu sunt statistici de vârstă pentru ziua de azi"
    get_kwargs = {"slug": "romania-slug"}

    @mock.patch("core.database.get_stats")
    @mock.patch("core.local_data.DLZArchiveSerializer")
    @mock.patch("core.local_data.formatters.parse_global")
    def test_with_stats(self, parse_mock, ser, get_mock):
        ser.deserialize.return_value = {
            "Categorii de vârstă": {"0-1": 1},
            "Data": "la",
        }
        parse_mock.return_value = "foo"
        assert local_data.local_age() == "foo"
        get_mock.assert_called_once_with(slug="romania-slug")
        parse_mock.assert_called_once_with(
            emoji="🦠",
            footer="\n`Actualizat la: la`",
            items=[],
            stats=["🦠 `0-1: 1`"],
            title="🇷🇴Categorii de vârstă",
        )
