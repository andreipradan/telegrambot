import logging


def dispatcher(*args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info(f"args: {args}\nkwargs: {kwargs}")
