from unittest import mock

from scrapers.client import BaseClient, DLZClient


@mock.patch("scrapers.client.requests")
def test_base_client_fetch(req):
    assert BaseClient().fetch() == req.get()


class TestDLZClient:
    @mock.patch("scrapers.client.requests")
    @mock.patch("scrapers.client.DLZSerializer")
    def test_fetch(self, ser, req):
        assert DLZClient().fetch() == {
            "Confirmați": req.get().json().__getitem__().__getitem__(),
            "Vindecați": req.get().json().__getitem__().__getitem__(),
            "Decedați": req.get().json().__getitem__().__getitem__(),
            "Actualizat la": req.get().json().__getitem__().__getitem__(),
            "Procent barbati": req.get().json().__getitem__().__getitem__(),
            "Procent femei": req.get().json().__getitem__().__getitem__(),
            "Procent copii": req.get().json().__getitem__().__getitem__(),
            "Vârstă medie": req.get().json().__getitem__().__getitem__(),
            "Categorii de vârstă": req.get()
            .json()
            .__getitem__()
            .__getitem__(),
            "Judete": req.get().json().__getitem__().__getitem__(),
        }
