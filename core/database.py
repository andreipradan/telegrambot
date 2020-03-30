import os
from pymongo import MongoClient

# from pymongo import UpdateOne

from core.constants import COLLECTION
from core.constants import DEFAULT_DB
from core.constants import SLUG


def get_client(db_host=None):
    return MongoClient(db_host or os.environ["MONGO_DB_HOST"])


def get_collection(name, client=None):
    client = client or get_client
    return client()[DEFAULT_DB][name]


def get_etag():
    return get_collection(COLLECTION["etag"]).find_one({"slug": SLUG["etag"]})


def get_stats(collection=COLLECTION["romania"], slug=SLUG["romania"]):
    stats = get_collection(collection).find_one({"slug": slug})
    if stats:
        stats.pop("_id")
        stats.pop("slug")
    return stats


def set_stats(stats, collection=COLLECTION["romania"], slug=SLUG["romania"]):
    get_collection(collection).update_one(
        {"slug": slug}, update={"$set": stats}, upsert=True,
    )


def get_many(collection, order_by=None, how=-1):
    result = get_collection(collection).find()
    if order_by:
        return result.sort(order_by, how)
    return result
