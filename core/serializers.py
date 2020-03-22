from collections import OrderedDict

from core.constants import COUNTY_FIELDS, RO_FIELDS


class BaseSerializer:
    fields = NotImplemented
    ignore_fields = ['_id', 'OBJECTID']

    def serialize(self, data):
        result = OrderedDict()
        for field in self.fields:
            if field not in self.ignore_fields:
                result[field] = data[field]
        return result

    def __init__(self, data):
        self.data = self.serialize(data) if not isinstance(data, list) else [
            self.serialize(item) for item in data
        ]


class CountySerializer(BaseSerializer):
    fields = [item for item in COUNTY_FIELDS if item != 'Judete'] + ['slug']


class CountyConfirmedSerializer(BaseSerializer):
    fields = 'slug', 'Cazuri_confirmate'


class CountrySerializer(BaseSerializer):
    fields = RO_FIELDS
    ignore_fields = BaseSerializer.ignore_fields + ['slug']
