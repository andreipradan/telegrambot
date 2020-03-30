import base64
import enum
import json
import logging
import os

from pymongo import UpdateOne

from core import database, constants
from scrapers import global_


class AllowedTypes(enum.Enum):
    DATE_LA_ZI = "datelazi"
    STIRI_OFICIALE = "stirioficiale"
    WORLDOMETERS = "worldometers"


def set_multiple(data, collection):
    return collection.bulk_write(
        [
            UpdateOne(
                {"country": country}, update={"$set": data}, upsert=True,
            )
            for country, data in data.items()
        ]
    )


def dispatcher(event, *_):
    logger = logging.getLogger(__name__)

    payload = json.loads(base64.b64decode(event["data"]).decode("utf-8"))

    run_type = payload["type"]
    if run_type not in AllowedTypes:
        return logger.error(f"Bad payload received: {payload}")

    if run_type == AllowedTypes.WORLDOMETERS:
        data = global_(text=210, json=True)
        collection = database.get_collection(
            constants.COLLECTION["global"],
            client=database.get_client(os.environ["DB_HOST"]),
        )
        results = ""
        results += str(
            collection.update_one(
                {"slug": constants.SLUG["global"]},
                update={"$set": data["top_stats"]},
                upsert=True,
            )
        )
        results += set_multiple(data["countries"], collection)
        return logger.info(f"Completed! Results: {results}")
    return logger.error("Coming soon...")
