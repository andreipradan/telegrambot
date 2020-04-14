import logging

import requests

from core import database
from core.constants import SLUG, COLLECTION
from core.validators import is_valid_date
from serializers import DLZSerializer, DLZArchiveSerializer

logger = logging.getLogger(__name__)


class DateLaZiClient:
    slug = SLUG["romania"]
    url = "https://api1.datelazi.ro/api/v2/data/"

    def __init__(self):
        self._local_data = None
        self._remote_data = None
        self.serialized_data = None

    def _fetch_remote(self):
        response = requests.get(url=self.url)
        response.raise_for_status()
        self._remote_data = response.json()
        return self._remote_data

    def sync(self, serializer_class=DLZSerializer, sub_bloc="currentDayStats"):
        remote_data = self._fetch_remote()
        serializer = serializer_class(remote_data[sub_bloc])

        data = serializer.data
        self.serialized_data = data
        self._local_data = database.get_stats(slug=self.slug)
        if self._local_data and data.items() <= self._local_data.items():
            msg = "Today: No updates"
            logger.info(msg)
            return

        serializer.save()
        logger.info("Today: Completed")

    def sync_archive(self):
        if not self._remote_data:
            self._fetch_remote()

        historical_data = self._remote_data["historicalData"]
        updated = False
        for day in [date for date in historical_data if is_valid_date(date)]:
            serializer = DLZArchiveSerializer(historical_data[day])
            db_stats = database.get_stats(COLLECTION["archive"], Data=day)
            if db_stats and serializer.data.items() <= db_stats.items():
                continue

            serializer.save()
            logger.info(f"Archive: Updated {day}")
            updated = True

        logger.info(f"Archive: {'Completed' if updated else 'No updates'}")
