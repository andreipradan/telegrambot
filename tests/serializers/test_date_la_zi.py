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
    excluded_fields = "complete", "fileName", "parsedOnString"
    db_payload = DB_PAYLOAD
    serializer = DLZSerializer
    serialize_fields = (
        ("averageAge", "Vârstă medie"),
        ("distributionByAge", "Categorii de vârstă"),
        ("numberCured", "Vindecați"),
        ("numberDeceased", "Decedați"),
        ("numberInfected", "Confirmați"),
        ("parsedOn", "Actualizat la"),
        ("percentageOfWomen", "Procent femei"),
        ("percentageOfMen", "Procent barbati"),
        ("percentageOfChildren", "Procent copii"),
    )

    def test_fields(self):
        assert self.serializer.excluded_fields == self.excluded_fields
        assert self.serializer.serialize_fields == self.serialize_fields

    def test_serialize(self):
        assert self.serializer.serialize(API_PAYLOAD) == self.db_payload

    def test_deserializer(self):
        assert self.serializer.deserialize(DB_PAYLOAD) == {
            "Vârstă medie": "46",
            "Actualizat la": "2020-04-03 17:22:00 EEST",
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


class TestDLZArchiveSerializer(TestDLZSerializer):
    excluded_fields = "complete", "fileName"
    serializer = DLZArchiveSerializer
    serialize_fields = TestDLZSerializer.serialize_fields + (
        ("parsedOnString", "Data"),
    )

    @property
    def db_payload(self):
        payload = deepcopy(DB_PAYLOAD)
        payload["Data"] = "2020-04-03"
        return payload
