from typing import List, Optional

from pynamodb.exceptions import DoesNotExist

from chalicelib.models.db import UserModel
from chalicelib.utils import ms_since_epoch


def create_user(
    parent_geohash: str,
    distance: int,
    zipcode: str,
    email: str,
    state_abbr: str,
    timezone: str,
) -> UserModel:
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
            updated_at=updated_at,
        ),
        distance=distance,
        zipcode=zipcode,
        state_abbr=state_abbr,
        timezone=timezone,
        updated_at=updated_at,
    )
    user.save()
    return user


def load_user_by_email(email: str) -> Optional[UserModel]:
    """
    Loads a user from the database
    """
    try:
        user = UserModel.get(email)
        return user
    except DoesNotExist:
        return None


def load_users_by_parent_geohash_distance(
    parent_geohash: str,
    distance: int,
) -> List[UserModel]:
    return list(
        UserModel.location_index.query(
            parent_geohash,
            UserModel.distance_zipcode.startswith(f"{distance}+"),
        ),
    )
