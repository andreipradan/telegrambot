import os
from pymongo import MongoClient

from core.constants import COLLECTION

DATABASE_NAME = os.getenv("DATABASE_NAME")


def get_client(db_host=None):
    if not DATABASE_NAME:
        raise ValueError("DATABASE_NAME env variable required")
    return MongoClient(db_host or os.environ["MONGO_DB_HOST"])


def get_collection(name, client=None):
    client = client or get_client
    return client()[DATABASE_NAME][name]


def get_stats(collection=COLLECTION["romania"], **kwargs):
    if not kwargs:
        raise ValueError("filter kwargs required")
    stats = get_collection(collection).find_one(kwargs)
    if stats:
        stats.pop("_id")
        stats.pop("slug", None)
    return stats


def set_stats(stats, collection=COLLECTION["romania"], **filter_kwargs):
    if not filter_kwargs:
        raise ValueError("filter kwargs required")
    get_collection(collection).update_one(
        filter_kwargs, update={"$set": stats}, upsert=True,
    )


def get_many(collection, order_by=None, how=-1):
    result = get_collection(collection).find()
    if order_by:
        return result.sort(order_by, how)
    return result
