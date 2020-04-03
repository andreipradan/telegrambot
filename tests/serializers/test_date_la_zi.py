from collections import OrderedDict
from copy import deepcopy

from serializers.date_la_zi import DLZSerializer, DLZArchiveSerializer

API_PAYLOAD = {
    "complete": True,
    "parsedOn": 1585923720,
    "parsedOnString": "2020-04-03",
    "fileName": "",
    "averageAge": "46",
    "numberInfected": 3183,
    "numberCured": 283,
    "numberDeceased": 133,
    "percentageOfWomen": 55,
    "percentageOfMen": 41,
    "percentageOfChildren": 4,
    "distributionByAge": {
        "0-9": 30,
        "10-19": 47,
        "20-29": 165,
        "30-39": 337,
        "40-49": 501,
        "50-59": 373,
        "60-69": 228,
        "70-79": 126,
        ">80": 29,
        "în procesare": 116,
    },
}


DB_PAYLOAD = {
    "Actualizat la": 1585923720,
    "Data": "2020-04-03",
    "Vârstă medie": "46",
    "Confirmați": 3183,
    "Vindecați": 283,
    "Decedați": 133,
    "Procent femei": 55,
    "Procent barbati": 41,
    "Procent copii": 4,
    "Categorii de vârstă": {
        "0-9": 30,
        "10-19": 47,
        "20-29": 165,
        "30-39": 337,
        "40-49": 501,
        "50-59": 373,
        "60-69": 228,
        "70-79": 126,
        ">80": 29,
        "în procesare": 116,
    },
}


class TestDLZSerializer:
    db_payload = OrderedDict(
        {
            "Confirmați": 3183,
            "Vindecați": 283,
            "Decedați": 133,
            "Actualizat la": 1585923720,
        }
    )
    deserialized = {
        "Confirmați": 3183,
        "Vindecați": 283,
        "Decedați": 133,
        "Actualizat la": "2020-04-03 17:22",
    }
    serializer = DLZSerializer
    mapped_fields = {
        "Confirmați": "numberInfected",
        "Vindecați": "numberCured",
        "Decedați": "numberDeceased",
        "Actualizat la": "parsedOn",
    }

    def test_fields(self):
        assert self.serializer.mapped_fields == self.mapped_fields

    def test_serialize(self):
        assert self.serializer(API_PAYLOAD).data == self.db_payload

    def test_deserializer(self):
        assert self.serializer.deserialize(DB_PAYLOAD) == self.deserialized


class TestDLZArchiveSerializer(TestDLZSerializer):
    db_payload = {
        "Data": "2020-04-03",
        "Vârstă medie": "46",
        "Actualizat la": 1585923720,
        "Confirmați": 3183,
        "Vindecați": 283,
        "Decedați": 133,
        "Procent femei": 55,
        "Procent barbati": 41,
        "Procent copii": 4,
        "Categorii de vârstă": {
            "0-9": 30,
            "10-19": 47,
            "20-29": 165,
            "30-39": 337,
            "40-49": 501,
            "50-59": 373,
            "60-69": 228,
            "70-79": 126,
            ">80": 29,
            "în procesare": 116,
        },
    }
    deserialized = {
        "Data": "2020-04-03",
        "Vârstă medie": "46",
        "Actualizat la": "2020-04-03 17:22",
        "Confirmați": 3183,
        "Vindecați": 283,
        "Decedați": 133,
        "Procent femei": 55,
        "Procent barbati": 41,
        "Procent copii": 4,
        "Categorii de vârstă": {
            "0-9": 30,
            "10-19": 47,
            "20-29": 165,
            "30-39": 337,
            "40-49": 501,
            "50-59": 373,
            "60-69": 228,
            "70-79": 126,
            ">80": 29,
            "în procesare": 116,
        },
    }
    serializer = DLZArchiveSerializer
    mapped_fields = {
        "Data": "parsedOnString",
        "Vârstă medie": "averageAge",
        "Categorii de vârstă": "distributionByAge",
        "Vindecați": "numberCured",
        "Decedați": "numberDeceased",
        "Confirmați": "numberInfected",
        "Actualizat la": "parsedOn",
        "Procent femei": "percentageOfWomen",
        "Procent barbati": "percentageOfMen",
        "Procent copii": "percentageOfChildren",
    }
