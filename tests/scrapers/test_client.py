from unittest import mock

from scrapers.clients.datelazi import DateLaZiClient


class TestDLZClient:
    @mock.patch("scrapers.clients.datelazi.requests")
    def test_fetch(self, req):
        assert DateLaZiClient()._fetch_remote() == req.get().json()
