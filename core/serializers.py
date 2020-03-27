from collections import OrderedDict


class BaseSerializer:
    block = NotImplemented
    fields = NotImplemented
    ignore_fields = ['_id', 'OBJECTID']

    def get_block(self, data):
        while self.block:
            attr = self.block.split('.').pop(0)
            self.block = '.'.join(self.block.split('.')[1:])
            return self.get_block(data[attr])
        return data

    def serialize(self, data):
        data = self.get_block(data)
        result = OrderedDict()
        for field in self.fields:
            if field not in self.ignore_fields:
                result[field] = data[field]
        return result

    def __init__(self, data):
        self.data = self.serialize(data) if not isinstance(data, list) else [
            self.serialize(item) for item in data
        ]


class HistogramSerializer(BaseSerializer):
    block = 'ageHistogram.histogram'
