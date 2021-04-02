from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute
import os


class UserIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user-index'
        projection = AllProjection()
        read_capacity_units = 5
        write_capacity_units = 5

    email = UnicodeAttribute(hash_key=True)


class NotificationModel(Model):
    class Meta:
        table_name = os.environ['DYNAMO_DB_TABLE_NAME']
        read_capacity_units = 20
        write_capacity_units = 5

    zipcode = UnicodeAttribute(hash_key=True)
    miles_updated_at = UnicodeAttribute(range_key=True)
    email = UnicodeAttribute()

    user_index = UserIndex()
