from pynamodb.models import DoesNotExist

from chalicelib.models.db import UserModel
from chalicelib.utils import ms_since_epoch
from typing import Optional, List, Iterator
from chalicelib.logs.decorators import func_time


def create_user(email: str, zipcode: str, distance: int) -> UserModel:
    """
    Creates a user
    """
    user = UserModel(
        email=email,
        zipcode_distance=f'{zipcode}+{distance}',
        updated_at=ms_since_epoch(),
    )
    user.save()
    user.refresh()
    return user


def delete_user_by_email(email: str) -> Optional[UserModel]:
    """
    Loads a user from the database and deletes them
    """
    user = load_user_by_email(email)
    if not user:
        return None

    user.delete()
    return user


@func_time
def load_user_by_email(email: str) -> Optional[UserModel]:
    """
    Loads a user from the database
    """
    try:
        user = UserModel.get(email)
        return user
    except DoesNotExist:
        return None


@func_time
def batch_get_users_by_zipcode_distance(
    zipcodes: List[str],
    distance: str,
) -> Iterator[UserModel]:
    keys = [f'{zipcode}+{distance}' for zipcode in zipcodes]
    return UserModel.zipcode_distance_index.batch_get(keys)
