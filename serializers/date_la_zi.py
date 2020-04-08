from collections import OrderedDict
from datetime import datetime
import pytz

from core import database
from core.constants import COLLECTION, SLUG


def epoch_to_timezone(epoch):
    utc_dt = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    tz = pytz.timezone("Europe/Bucharest")
    dt = utc_dt.astimezone(tz)

    return dt.strftime("%H:%M, %d %b %Y")


class DLZSerializer:
    epoch_time_fields = ("Actualizat la",)
    mapped_fields = {
        "Confirmați": "numberInfected",
        "Vindecați": "numberCured",
        "Decedați": "numberDeceased",
        "Actualizat la": "parsedOn",
        "Procent barbati": "percentageOfMen",
        "Procent femei": "percentageOfWomen",
        "Procent copii": "percentageOfChildren",
        "Vârstă medie": "averageAge",
        "Categorii de vârstă": "distributionByAge",
        "Judete": "countyInfectionsNumbers",
    }
    deserialize_fields = "Confirmați", "Vindecați", "Decedați", "Actualizat la"

    def __init__(self, response):
        self.response = response
        self.data = OrderedDict()
        for field, api_field in self.mapped_fields.items():
            self.data[field] = self.response[api_field]

    def save(self):
        database.set_stats(
            stats=self.data,
            collection=COLLECTION["romania"],
            slug=SLUG["romania"],
        )

    @classmethod
    def deserialize(cls, data):
        results = OrderedDict()
        for key in cls.deserialize_fields:
            results[key] = cls.deserialize_field(key, data[key])
        return results

    @classmethod
    def deserialize_field(cls, key, value):
        if key in cls.epoch_time_fields:
            return epoch_to_timezone(value)
        return value


class DLZArchiveSerializer(DLZSerializer):
    mapped_fields = {
        "Confirmați": "numberInfected",
        "Vindecați": "numberCured",
        "Decedați": "numberDeceased",
        "Actualizat la": "parsedOn",
        "Data": "parsedOnString",
        "Procent barbati": "percentageOfMen",
        "Procent femei": "percentageOfWomen",
        "Procent copii": "percentageOfChildren",
        "Vârstă medie": "averageAge",
        "Categorii de vârstă": "distributionByAge",
        "Judete": "countyInfectionsNumbers",
    }
    deserialize_fields = list(mapped_fields)

    def save(self):
        database.set_stats(
            stats=self.data,
            collection=COLLECTION["archive"],
            Data=self.data["Data"],
        )
