from collections import OrderedDict

from core.constants import COUNTY_FIELDS, RO_FIELDS


class BaseSerializer:
    fields = NotImplemented
    ignore_fields = ['_id', 'OBJECTID']

    def __init__(self, data):
        result = OrderedDict()
        for field in self.fields:
            if field not in self.ignore_fields:
                result[field] = data[field]
        self.data = result


class CountySerializer(BaseSerializer):
    fields = COUNTY_FIELDS


class CountrySerializer(BaseSerializer):
    fields = RO_FIELDS
    ignore_fields = BaseSerializer.ignore_fields + ['slug']
