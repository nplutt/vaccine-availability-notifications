from chalice import ConflictError

from chalicelib.logs.utils import get_logger
from chalicelib.models.api import UserSchema
from chalicelib.models.db import UserModel
from chalicelib.repositories.user_repository import (
    create_user,
    load_user_by_email,
)
from chalicelib.services.geo_service import get_zipcode_parent_geohash


logger = get_logger(__name__)


def create_new_user(body: UserSchema) -> UserModel:
    if load_user_by_email(body.email):
        logger.error("User with email already exists!")
        raise ConflictError

    return create_user(
        parent_geohash=get_zipcode_parent_geohash(body.zipcode),
        distance=body.distance,
        zipcode=body.zipcode,
        email=body.email,
    )
