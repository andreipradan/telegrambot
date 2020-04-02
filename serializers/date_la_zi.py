class BaseSerializer:
    @staticmethod
    def serialize():
        return NotImplementedError

    @staticmethod
    def to_telegram():
        return NotImplementedError


class DLZSerializer:
    pass


class DLZArchiveSerializer:
    pass


aaa = {
    "_id": {"$oid": "5e851916553d0aed0f3b67a4"},
    "parsedOnString": "2020-03-31",
    "averageAge": "46",
    "complete": True,
    "distributionByAge": {
        "0-9": {"$numberInt": "30"},
        "10-19": {"$numberInt": "47"},
        "20-29": {"$numberInt": "165"},
        "30-39": {"$numberInt": "337"},
        "40-49": {"$numberInt": "501"},
        "50-59": {"$numberInt": "373"},
        "60-69": {"$numberInt": "228"},
        "70-79": {"$numberInt": "126"},
        ">80": {"$numberInt": "29"},
        "în procesare": {"$numberInt": "116"},
    },
    "fileName": "",
    "numberCured": {"$numberInt": "220"},
    "numberDeceased": {"$numberInt": "82"},
    "numberInfected": {"$numberInt": "2245"},
    "parsedOn": {"$numberInt": "1585681080"},
    "percentageOfChildren": {"$numberDouble": "4"},
    "percentageOfMen": {"$numberDouble": "41"},
    "percentageOfWomen": {"$numberDouble": "55"},
}
