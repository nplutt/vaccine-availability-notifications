import asyncio
from typing import List

from chalice import ConflictError

from chalicelib.logs.decorators import func_time
from chalicelib.logs.utils import get_logger
from chalicelib.models.api import UserSchema
from chalicelib.models.db import UserModel
from chalicelib.repositories.user_repository import (
    create_user,
    load_user_by_email, load_users_by_parent_geohash_distance,
)
from chalicelib.services.email_service import logger
from chalicelib.services.geo_service import get_zipcode_parent_geohash, find_zipcodes_in_radius, \
    find_geohashes_in_radius
from chalicelib.utils import get_or_create_eventloop

logger = get_logger(__name__)


def create_new_user(body: UserSchema) -> UserModel:
    if load_user_by_email(body.email):
        logger.error("User with email already exists!")
        raise ConflictError

    return create_user(
        parent_geohash=get_zipcode_parent_geohash(body.zipcode, body.distance),
        distance=body.distance,
        zipcode=body.zipcode,
        email=body.email,
    )


@func_time
def find_users_to_notify_for_location(location: dict) -> None:
    coordinates = location["geometry"]["coordinates"]
    coordinates.reverse()

    if None in coordinates:
        return None

    zipcode_distances = find_zipcodes_in_radius(coordinates[0], coordinates[1], 50)
    for distance, zipcodes in zipcode_distances.items():
        parent_geohashes = find_geohashes_in_radius(coordinates[0], coordinates[1], distance)

        users = []
        filtered_user_count = 0
        zipcode_set = set(zipcodes)
        for geohash in parent_geohashes:
            unfiltered_users = load_users_by_parent_geohash_distance(geohash, distance)
            filtered_users = list(
                filter(lambda u: u.zipcode in zipcode_set, unfiltered_users),
            )
            filtered_user_count += len(unfiltered_users) - len(filtered_users)
            users += filtered_users

        logger.info(
            "Retrieved users from DynamoDB",
            extra={
                "users": len(users),
                "filtered_users": filtered_user_count,
                "zipcodes": len(zipcode_set),
                "distance": distance,
            },
        )


async def bulk_notify_users(locations: List[dict]) -> None:
    loop = get_or_create_eventloop()
    futures = [
        loop.run_in_executor(None, find_users_to_notify_for_location, location) for location in locations
    ]
    for res in await asyncio.gather(*futures):
        pass