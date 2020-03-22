import os
from pymongo import MongoClient, UpdateOne

from core.constants import COLLECTION, DEFAULT_DB, SLUG


def get_client():
    return MongoClient(os.environ['MONGO_DB_HOST'])


def get_collection(name, client=get_client()):
    return client[DEFAULT_DB][name]


def get_etag():
    return get_collection(COLLECTION['etag']).find_one({'slug': SLUG['etag']})


def get_all(collection):
    return list(get_collection(collection).find())


def get_stats(collection, slug):
    return get_collection(collection).find_one({'slug': slug})


def set_etag(etag):
    return get_collection(COLLECTION['etag']).update_one(
        filter={'slug': SLUG['etag']},
        update={'$set': {'value': etag}},
        upsert=True,
    )


def set_multiple(data, collection=COLLECTION['counties']):
    return get_collection(collection).bulk_write(
        [
            UpdateOne(
                {'slug': item.pop('Judete')},
                update={'$set': item},
                upsert=True
            ) for item in data
        ]
    )


def set_stats(slug, stats, collection=COLLECTION['romania']):
    get_collection(collection).update_one(
        {'slug': slug},
        update={'$set': stats},
        upsert=True,
    )
