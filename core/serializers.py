from collections import OrderedDict


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


class TotalSerializer(BaseSerializer):
    fields = ('Cazuri_confirmate', 'Decedati', 'Last_updated')
    ignore_fields = ('FID', 'column0')
