import logging
import os

import requests

from core import database
from core.constants import SLUG, COLLECTION
from core.validators import is_valid_date
from scrapers.clients.utils import get_date_from_archive
from serializers import (
    DLZSerializer,
    DLZArchiveSerializer,
    DLZArchiveSmallSerializer,
)

logger = logging.getLogger(__name__)


class DateLaZiClient:
    slug = SLUG["romania"]
    url = os.environ["DATELAZI_DATA_URL"]
    small_archive = url.endswith("smallData.json")

    def __init__(self):
        self._local_data = None
        self.serialized_data = None

    def _fetch_archive(self, days):
        archive_collection = (
            f"archive{'-small' if self.small_archive  else ''}"
        )
        return list(
            database.get_collection(COLLECTION[archive_collection]).find(
                {"Data": {"$in": days}},
                sort=[("Data", -1)],
            )
        )

    def _fetch_local(self):
        self._local_data = database.get_stats(slug=self.slug)
        return self._local_data

    def _fetch_remote(self):
        response = requests.get(url=self.url)
        response.raise_for_status()
        return response.json()

    def sync(self):
        remote_data = self._fetch_remote()
        serializer = DLZSerializer(remote_data["currentDayStats"])

        data = serializer.data
        self.serialized_data = data

        self._fetch_local()
        if self._local_data and data.items() <= self._local_data.items():
            msg = "Today: No updates"
            logger.info(msg)
            return

        serializer.save()
        logger.info("Today: Completed")

    def sync_archive(self):
        logger.info("Archive: No remote data, fetching...")
        data = self._fetch_remote()
        logger.info("Archive: Fetching completed")

        historical_data = data["historicalData"]

        valid_days = [d for d in historical_data if is_valid_date(d)]
        if not valid_days:
            logger.warning("Archive: No valid dates found in the API.")
            logger.info("Archive: Done")
            return

        logger.info("Archive: Fetching days from db...")
        archive = self._fetch_archive(list(valid_days))
        logger.info("Archive: Fetched")

        serializer_class = (
            DLZArchiveSmallSerializer
            if self.small_archive
            else DLZArchiveSerializer
        )

        updates = []
        for day in valid_days:
            day_data = historical_data[day]
            day_data["parsedOnString"] = day
            serializer = serializer_class(day_data)
            db_stats = get_date_from_archive(day, archive)
            if db_stats and serializer.data.items() <= db_stats.items():
                continue

            updates.append(serializer.save(commit=False))
            logger.info(f"[Archive] Day to update: {day}")
        if updates:
            database.bulk_update(serializer_class.collection, updates)
        else:
            logger.warning(f"Last 3 dates (API): {list(historical_data)[:3]}")

        logger.info(f"Archive: {'Completed' if updates else 'No updates'}")
