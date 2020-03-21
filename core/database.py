import os
from pymongo import MongoClient

DEFAULT_DB = 'telegrambot_db'
DEFAULT_COLLECTION = 'countries'


def get_client():
    return MongoClient(os.environ['MONGO_DB_HOST'])


def get_collection(collection=DEFAULT_COLLECTION, client=get_client()):
    client[DEFAULT_DB][DEFAULT_COLLECTION].create_index('slug', unique=True)
    return client[DEFAULT_DB][collection]


def update_or_create(**kwargs):
    assert 'slug' in kwargs
    collection = get_collection()
    return collection.update_one(
        {'slug': kwargs['slug']},
        update={'$set': kwargs},
        upsert=True
    )


def get_country(**kwargs):
    assert 'slug' in kwargs
    return get_collection().find(kwargs)
