from typing import Iterator, List, Optional
from pynamodb.exceptions import DoesNotExist


from chalicelib.logs.decorators import func_time
from chalicelib.models.db import UserModel
from chalicelib.utils import ms_since_epoch


def create_user(parent_geohash: str, distance: int, zipcode: str, email: str) -> UserModel:
    """
    Creates a user
    """
    updated_at = ms_since_epoch()
    user = UserModel(
        email=email,
        parent_geohash=parent_geohash,
        distance_zipcode=UserModel.build_distance_zipcode(
            distance=distance,
            zipcode=zipcode,
            updated_at=updated_at
        ),
        distance=distance,
        zipcode=zipcode,
        updated_at=updated_at,
    )
    user.save()
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
def load_users_by_parent_geohash_distance(
    parent_geohash: str,
    distance: int,
) -> List[UserModel]:
    return list(UserModel.location_index.query(
        parent_geohash,
        UserModel.distance_zipcode.startswith(f'{distance}+')
    ))
