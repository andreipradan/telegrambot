import base64
import json
import logging
import os


def dispatcher(event, context):
    logger = logging.getLogger(__name__)
    logger.info(f"event: {event} | context{context}")

    payload = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    logger.info(f"payload: {payload}")
