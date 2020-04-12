import requests

from serializers import DLZSerializer


class BaseClient:
    serializer_class = NotImplemented
    url = NotImplemented

    def __init__(self):
        self._serializer = None

    def fetch(self):
        response = requests.get(url=self.url)
        response.raise_for_status()
        return response


class DLZClient(BaseClient):
    serializer_class = DLZSerializer
    url = "https://api1.datelazi.ro/api/v2/data/"

    def fetch(self):
        response = super().fetch()
        json = response.json()
        self._serializer = self.serializer_class(json["currentDayStats"])
        return self._serializer.data

    @property
    def normalized_data(self):
        return self._serializer.deserialize(self._serializer.data)

    def store(self):
        return self._serializer.save()
