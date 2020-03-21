import os
from pymongo import MongoClient

DEFAULT_DB = 'telegrambot_db'
DEFAULT_COLLECTION = 'countries'


def get_client():
    return MongoClient(os.environ['MONGO_DB_HOST'])


def get_collection(collection=DEFAULT_COLLECTION, client=get_client()):
    client[DEFAULT_DB][DEFAULT_COLLECTION].create_index('slug', unique=True)
    return client[DEFAULT_DB][collection]


def get_romania_stats():
    return get_collection('top_stats').find_one({'slug': 'romania-stats'})


def set_romania_stats(**stats):
    get_collection('top_stats').update_one(
        {'slug': 'romania-stats'},
        update={'$set': stats},
        upsert=True,
    )
