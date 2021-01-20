from collections import OrderedDict
from unittest import mock

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
    "countyInfectionsNumbers": {
        "AB": 33,
        "AR": 150,
        "AG": 25,
        "BC": 38,
        "BH": 46,
        "BN": 42,
        "BT": 68,
        "BV": 131,
        "BR": 11,
        "BZ": 12,
        "CS": 21,
        "CL": 30,
        "CJ": 110,
        "CT": 114,
        "CV": 47,
        "DB": 23,
        "DJ": 27,
        "GL": 101,
        "GR": 24,
        "GJ": 8,
        "HR": 1,
        "HD": 124,
        "IL": 56,
        "IS": 88,
        "IF": 78,
        "MM": 42,
        "MH": 12,
        "MS": 57,
        "NT": 160,
        "OT": 11,
        "PH": 26,
        "SM": 21,
        "SJ": 8,
        "SB": 49,
        "SV": 1215,
        "TR": 21,
        "TM": 176,
        "TL": 6,
        "VS": 13,
        "VL": 8,
        "VN": 79,
        "B": 552,
    },
    "incidence": {"AB": 1.6, "BN": 2.1},
    "vaccines": {"comp1": {"total_administered": 12, "immunized": 23}},
    "numberTotalDosesAdministered": 991,
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
    "Categorii de vârstă": API_PAYLOAD["distributionByAge"],
    "Judete": API_PAYLOAD["countyInfectionsNumbers"],
    "Incidență": API_PAYLOAD["incidence"],
}


class TestDLZSerializer:
    db_payload = OrderedDict(
        {
            "Confirmați": 3183,
            "Vindecați": 283,
            "Decedați": 133,
            "Actualizat la": 1585923720,
            "Procent barbati": 41,
            "Procent femei": 55,
            "Procent copii": 4,
            "Vârstă medie": "46",
            "Categorii de vârstă": DB_PAYLOAD["Categorii de vârstă"],
            "Judete": DB_PAYLOAD["Judete"],
            "Incidență": DB_PAYLOAD["Incidență"],
            "Vaccinări": {
                "comp1": {"total_administered": 12, "immunized": 23}
            },
            "Total doze administrate": 991,
        }
    )
    deserialized = {
        "Confirmați": 3183,
        "Vindecați": 283,
        "Decedați": 133,
        "Actualizat la": "17:22, 03 Apr 2020",
    }
    serializer = DLZSerializer
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
        "Incidență": "incidence",
        "Vaccinări": "vaccines",
        "Total doze administrate": "numberTotalDosesAdministered",
    }

    def test_fields(self):
        assert self.serializer.mapped_fields == self.mapped_fields

    def test_serialize(self):
        assert self.serializer(API_PAYLOAD).data == self.db_payload

    def test_deserializer(self):
        assert self.serializer.deserialize(DB_PAYLOAD) == self.deserialized

    @mock.patch("core.database.set_stats")
    def test_save(self, set_stats):
        serializer = self.serializer(API_PAYLOAD)
        stats_kwargs = {
            "stats": self.db_payload,
        }
        if isinstance(serializer, DLZArchiveSerializer):
            stats_kwargs["collection"] = "romania-archive"
            stats_kwargs["Data"] = serializer.data["Data"]
        else:
            stats_kwargs["collection"] = "romania-collection"
            stats_kwargs["slug"] = "romania-slug"
        serializer.save()
        set_stats.assert_called_once_with(**stats_kwargs)


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
        "Categorii de vârstă": DB_PAYLOAD["Categorii de vârstă"],
        "Judete": DB_PAYLOAD["Judete"],
        "Incidență": DB_PAYLOAD["Incidență"],
    }
    deserialized = {
        "Data": "2020-04-03",
        "Vârstă medie": "46",
        "Actualizat la": "17:22, 03 Apr 2020",
        "Confirmați": 3183,
        "Vindecați": 283,
        "Decedați": 133,
        "Procent femei": 55,
        "Procent barbati": 41,
        "Procent copii": 4,
        "Categorii de vârstă": DB_PAYLOAD["Categorii de vârstă"],
        "Judete": DB_PAYLOAD["Judete"],
        "Incidență": DB_PAYLOAD["Incidență"],
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
        "Judete": "countyInfectionsNumbers",
        "Incidență": "incidence",
    }
