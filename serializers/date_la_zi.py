from collections import OrderedDict

from core import database
from core.constants import COLLECTION, SLUG
from core.utils import epoch_to_timezone


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
        self.data = OrderedDict()
        for field, api_field in self.mapped_fields.items():
            self.data[field] = response[api_field]

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
            return epoch_to_timezone(value).strftime("%H:%M, %d %b %Y")
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
