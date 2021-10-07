import logging
import os
from pymongo import MongoClient, UpdateOne

from core.constants import COLLECTION

logger = logging.getLogger(__name__)


def get_client():
    return MongoClient(host=os.getenv("MONGO_DB_HOST"))


def get_collection(name):
    return get_client()[os.getenv("DATABASE_NAME", "telegrambot_db")][name]


def get_stats(collection=COLLECTION["romania"], **kwargs):
    if not kwargs:
        raise ValueError("filter kwargs required")
    stats = get_collection(collection).find_one(kwargs)
    if stats:
        stats.pop("_id")
        stats.pop("slug", None)
    return stats


def set_stats(
    stats, collection=COLLECTION["romania"], commit=True, **filter_kwargs
):
    if not filter_kwargs:
        raise ValueError("filter kwargs required")

    update_params = {
        "filter": filter_kwargs,
        "update": {"$set": stats},
        "upsert": True,
    }
    if not commit:
        return UpdateOne(**update_params)

    return get_collection(collection).update_one(**update_params)


def get_many(collection, order_by=None, how=-1, **kwargs):
    result = get_collection(collection).find(kwargs)
    if order_by:
        return result.sort(order_by, how)
    return result


def bulk_update(collection, requests):
    logger.info(f"Saving {len(requests)} objects in {collection}")
    get_collection(collection).bulk_write(requests)
