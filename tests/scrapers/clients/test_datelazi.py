from unittest import mock

from scrapers.clients.datelazi import DateLaZiClient


class TestDLZClient:
    @mock.patch("scrapers.clients.datelazi.requests")
    def test_fetch(self, req):
        assert DateLaZiClient()._fetch_remote() == req.get().json()

    @mock.patch.object(
        DateLaZiClient, "_fetch_remote", lambda x: {"currentDayStats": {}}
    )
    @mock.patch("scrapers.clients.datelazi.logger")
    @mock.patch("core.database.get_stats")
    @mock.patch("scrapers.clients.datelazi.DLZSerializer")
    def test_sync_with_no_local_data(self, ser, get_stats, logger_mock):
        get_stats.return_value = {"foo": 1, "bar": 2}
        ser.return_value.data = {"foo": 1}
        assert DateLaZiClient().sync() is None
        get_stats.assert_called_once_with(slug="romania-slug")
        ser.assert_called_once_with({})
        logger_mock.info.assert_called_once_with("Today: No updates")
