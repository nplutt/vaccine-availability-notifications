import os

from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model


class ZipcodeDistanceIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "zipcode-distance-index"
        projection = AllProjection()
        read_capacity_units = 20
        write_capacity_units = 5

    zipcode_distance = UnicodeAttribute(hash_key=True)
    updated_at = NumberAttribute(range_key=True)


class UserModel(Model):
    class Meta:
        table_name = os.environ["DYNAMO_DB_TABLE_NAME"]
        read_capacity_units = 5
        write_capacity_units = 5

    email = UnicodeAttribute(hash_key=True)
    zipcode_distance = UnicodeAttribute()
    updated_at = NumberAttribute()

    zipcode_distance_index = ZipcodeDistanceIndex()
