import os
from unittest import mock

import pytest

from core import database, constants


class TestDatabase:
    @mock.patch("core.database.MongoClient", return_value="mongo_response")
    def test_get_client(self, monkeypatch):
        assert database.get_client() == "mongo_response"
        monkeypatch.assert_called_once_with(os.environ["MONGO_DB_HOST"])

    @mock.patch("core.database.get_client")
    def test_get_collection(self, client_mock):
        name = mock.MagicMock(return_value="foo")
        client_mock.return_value.__getitem__.return_value.__getitem__ = name
        assert database.get_collection("foo") == mock.ANY
        client_mock.assert_called_once_with()

    @mock.patch("core.database.get_collection")
    def test_get_etag(self, collection):
        collection.return_value.find_one.return_value = "etag_foo"
        assert database.get_etag() == "etag_foo"
        collection.assert_called_once_with(constants.COLLECTION["etag"])
        collection.return_value.find_one.assert_called_once_with(
            {"slug": constants.SLUG["etag"]}
        )

    @pytest.mark.parametrize(
        ("collection", "slug"), [(None, None), ("foo", "bar")]
    )
    @mock.patch("core.database.get_collection")
    def test_get_stats_with_no_stats(self, get_collection, collection, slug):
        get_collection.return_value.find_one.return_value = {}
        assert database.get_stats(collection, slug) == {}
        get_collection.assert_called_once_with(collection)
        get_collection.return_value.find_one.assert_called_once_with(
            {"slug": slug}
        )

    @mock.patch("core.database.get_collection")
    def test_get_stats_with_id_and_slug(self, get_collection):
        get_collection.return_value.find_one.return_value = {
            "_id": 1,
            "slug": 1,
            "foo": "bar",
        }
        assert database.get_stats() == {"foo": "bar"}

    @mock.patch("core.database.get_collection")
    def test_set_stats_default_params(self, collection):
        database.set_stats({"foo": "bar"})
        collection.assert_called_once_with(constants.COLLECTION["romania"])
        collection.return_value.update_one.assert_called_once_with(
            {"slug": constants.SLUG["romania"]},
            update={"$set": {"foo": "bar"}},
            upsert=True,
        )
