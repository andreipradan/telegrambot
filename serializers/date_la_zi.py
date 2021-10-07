from collections import OrderedDict
from datetime import datetime

from core import database
from core.constants import COLLECTION, SLUG, DATE_FORMAT


class DLZSerializer:
    collection = COLLECTION["romania"]
    date_fields = ("Data",)
    deserialize_fields = "Confirmați", "Vindecați", "Decedați", "Data"
    mapped_fields = {
        "Data": "parsedOnString",
        "Confirmați": "numberInfected",
        "Vindecați": "numberCured",
        "Decedați": "numberDeceased",
        "Procent barbati": "percentageOfMen",
        "Procent femei": "percentageOfWomen",
        "Procent copii": "percentageOfChildren",
        "Vârstă medie": "averageAge",
        "Categorii de vârstă": "distributionByAge",
        "Judete": "countyInfectionsNumbers",
        "Incidență": "incidence",
        "Vaccinări": "vaccines",
        "Total doze administrate": "numberTotalDosesAdministered",
    }

    def __init__(self, response):
        self.data = OrderedDict()
        for field, api_field in self.mapped_fields.items():
            self.data[field] = response.get(api_field)

    def save(self, commit=True):
        return database.set_stats(
            stats=self.data,
            collection=self.collection,
            commit=commit,
            slug=SLUG["romania"],
        )

    @classmethod
    def deserialize(cls, data, fields=None):
        if not fields:
            fields = cls.deserialize_fields
        results = OrderedDict()
        for key in fields:
            results[key] = cls.deserialize_field(key, data[key])
        return results

    @classmethod
    def deserialize_field(cls, key, value):
        if key in cls.date_fields:
            return datetime.strptime(value, DATE_FORMAT).strftime("%d %b %Y")
        return value


class DLZArchiveSerializer(DLZSerializer):
    collection = COLLECTION["archive"]
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
        "Incidență": "incidence",
    }
    deserialize_fields = list(mapped_fields)

    def save(self, commit=True):
        return database.set_stats(
            stats=self.data,
            collection=self.collection,
            commit=commit,
            Data=self.data["Data"],
        )


class DLZArchiveSmallSerializer(DLZSerializer):
    collection = COLLECTION["archive-small"]
    mapped_fields = {
        "Data": "parsedOnString",
        "Confirmați": "numberInfected",
        "Vindecați": "numberCured",
        "Decedați": "numberDeceased",
        "Categorii de vârstă": "distributionByAge",
        "Vaccinari": "vaccines",
    }
    deserialize_fields = list(mapped_fields)

    def save(self, commit=True):
        return database.set_stats(
            stats=self.data,
            collection=self.collection,
            commit=commit,
            Data=self.data["Data"],
        )
