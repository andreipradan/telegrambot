import os
from pymongo import MongoClient

# from pymongo import UpdateOne

from core.constants import COLLECTION
from core.constants import DEFAULT_DB
from core.constants import SLUG


def get_client():
    return MongoClient(os.environ["MONGO_DB_HOST"])


def get_collection(name):
    return get_client()[DEFAULT_DB][name]


def get_etag():
    return get_collection(COLLECTION["etag"]).find_one({"slug": SLUG["etag"]})


def get_stats(collection=COLLECTION["romania"], slug=SLUG["romania"]):
    stats = get_collection(collection).find_one({"slug": slug})
    if stats:
        stats.pop("_id")
        stats.pop("slug")
    return stats


# def set_etag(etag):
#     return get_collection(COLLECTION["etag"]).update_one(
#         filter={"slug": SLUG["etag"]},
#         update={"$set": {"value": etag}},
#         upsert=True,
#     )
#
#
# def set_multiple(data, collection=COLLECTION['romania']):
#     return get_collection(collection).bulk_write(
#         [
#             UpdateOne(
#                 {'slug': item.pop('Judete')},
#                 update={'$set': item},
#                 upsert=True
#             ) for item in data
#         ]
#     )


def set_stats(stats, collection=COLLECTION["romania"], slug=SLUG["romania"]):
    get_collection(collection).update_one(
        {"slug": slug}, update={"$set": stats}, upsert=True,
    )
