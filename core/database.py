import os
from pymongo import MongoClient

DEFAULT_DB = 'telegrambot_db'


def get_client():
    return MongoClient(os.environ['MONGO_DB_HOST'])


def get_collection(name, client=get_client()):
    client[DEFAULT_DB][name].create_index('slug', unique=True)
    return client[DEFAULT_DB][name]


def get_romania_stats():
    return get_collection('top_stats').find_one({'slug': 'romania-stats'})


def set_romania_stats(**stats):
    get_collection('top_stats').update_one(
        {'slug': 'romania-stats'},
        update={'$set': stats},
        upsert=True,
    )


def get_etag():
    return get_collection('etag').find_one({'slug': 'global_etag'})


def set_etag(etag):
    return get_collection('etag').update_one(
        filter={'slug': 'global_etag'},
        update={'$set': {'value': etag}},
        upsert=True,
    )
