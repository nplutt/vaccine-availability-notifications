import os

from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

from chalicelib.utils import ms_since_epoch, str_uuid


class LocationIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "location-index"
        region = os.environ["REGION"]
        projection = AllProjection()
        read_capacity_units = 75
        write_capacity_units = 5

    parent_geohash = UnicodeAttribute(hash_key=True)
    distance_zipcode = UnicodeAttribute(range_key=True)


class UserModel(Model):
    class Meta:
        table_name = os.environ["DYNAMO_DB_TABLE_NAME"]
        region = os.environ["REGION"]
        read_capacity_units = 5
        write_capacity_units = 5

    email = UnicodeAttribute(hash_key=True)
    parent_geohash = UnicodeAttribute()
    distance_zipcode = UnicodeAttribute()
    distance = NumberAttribute()
    zipcode = UnicodeAttribute()
    state_abbr = UnicodeAttribute()
    timezone = UnicodeAttribute()
    updated_at = NumberAttribute()

    location_index = LocationIndex()

    def update_keys(self) -> None:
        self.updated_at = ms_since_epoch()
        self.distance_zipcode = f"{self.distance}+{self.zipcode}+{self.updated_at}+{str_uuid().split('-')[4]}"
