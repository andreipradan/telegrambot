from copy import deepcopy
from datetime import datetime
import pytz


def epoch_to_timezone(epoch):
    utc_dt = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    tz = pytz.timezone("Europe/Bucharest")
    dt = utc_dt.astimezone(tz)

    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


class DLZSerializer:
    epoch_time_fields = ("Actualizat la",)
    excluded_fields = "complete", "fileName", "parsedOnString"
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

    @classmethod
    def serialize(cls, data):
        data = deepcopy(data)
        for field in cls.excluded_fields:
            data.pop(field, None)
        for key in deepcopy(data):
            data[dict(cls.serialize_fields)[key]] = data.pop(key)
        return data

    @classmethod
    def deserialize(cls, data):
        data = deepcopy(data)
        for key, value in data.items():
            data[key] = cls.deserialize_field(key, value)
        return data

    @classmethod
    def deserialize_field(cls, key, value):
        if key in cls.epoch_time_fields:
            return epoch_to_timezone(value)
        return value


class DLZArchiveSerializer(DLZSerializer):
    epoch_time_fields = DLZSerializer.epoch_time_fields + ("Data",)
    excluded_fields = "complete", "fileName"
    serialize_fields = DLZSerializer.serialize_fields + (
        ("parsedOnString", "Data"),
    )
