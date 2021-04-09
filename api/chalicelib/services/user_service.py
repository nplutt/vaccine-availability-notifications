import asyncio
from typing import Dict, List, Optional

import zipcodes
from chalice import ConflictError, NotFoundError

from chalicelib.logs.decorators import func_time
from chalicelib.logs.utils import get_logger
from chalicelib.models.api import UserSchema
from chalicelib.models.db import UserModel
from chalicelib.models.dto import UserEmailDTO
from chalicelib.repositories.user_repository import (
    create_user,
    load_user_by_email,
    load_users_by_parent_geohash_distance,
)
from chalicelib.services.email_service import logger
from chalicelib.services.geo_service import (
    find_geohashes_in_radius,
    find_zipcodes_in_radius,
    get_zipcode_parent_geohash,
)
from chalicelib.utils import get_or_create_eventloop
from chalicelib.enums.EmailTemplate import EmailTemplate
from chalicelib.services.email_service import send_emails_to_users


logger = get_logger(__name__)


def create_new_user(body: UserSchema) -> UserModel:
    if load_user_by_email(body.email):
        logger.error("User with email already exists!")
        raise ConflictError

    zipcode_info = zipcodes.matching(body.zipcode)[0]
    user = create_user(
        parent_geohash=get_zipcode_parent_geohash(body.zipcode, body.distance),
        distance=body.distance,
        zipcode=body.zipcode,
        email=body.email,
        state_abbr=zipcode_info["state"],
        timezone=zipcode_info["timezone"],
    )

    user_dto = UserEmailDTO.from_user(user)
    send_emails_to_users([user_dto], EmailTemplate.WELCOME)

    return user


def fetch_user(email: str) -> UserModel:
    user = load_user_by_email(email)
    if not user:
        raise NotFoundError

    return user


def update_user(body: UserSchema, user: UserModel) -> UserModel:
    user.zipcode = body.zipcode
    user.distance = body.distance
    user.parent_geohash = get_zipcode_parent_geohash(body.zipcode, body.distance)
    user.update_keys()
    user.save()
    return user


def delete_user(user: UserModel) -> UserModel:
    user.delete()
    return user


@func_time
def find_users_to_notify_for_location(location: dict) -> Optional[List[dict]]:
    coordinates = location["geometry"]["coordinates"]
    coordinates.reverse()

    if None in coordinates:
        return None

    users = []
    zipcode_distances = find_zipcodes_in_radius(coordinates[0], coordinates[1], 50)

    for distance, zipcodes in zipcode_distances.items():
        parent_geohashes = find_geohashes_in_radius(
            coordinates[0],
            coordinates[1],
            distance,
        )

        zipcode_set = set(zipcodes)
        for geohash in parent_geohashes:
            unfiltered_users = load_users_by_parent_geohash_distance(geohash, distance)
            filtered_users = list(
                filter(lambda u: u.zipcode in zipcode_set, unfiltered_users),
            )
            users += [
                {
                    "distance": zipcodes[u.zipcode],
                    "user": u,
                }
                for u in filtered_users
            ]

    return users


async def find_users_to_notify_for_locations(
    locations: List[dict],
) -> List[UserEmailDTO]:
    loop = get_or_create_eventloop()
    futures = [
        loop.run_in_executor(None, find_users_to_notify_for_location, location)
        for location in locations
    ]
    users_to_notify_for_locations = await asyncio.gather(*futures)

    user_map: Dict[str, UserEmailDTO] = {}
    for location, users in zip(locations, users_to_notify_for_locations):
        if users is None:
            continue

        for user in users:
            user_email = user["user"].email
            user_dto = user_map.get(user_email)
            if user_dto is None:
                user_dto = UserEmailDTO.from_user(user["user"])
                user_map[user_email] = user_dto

            user_dto.add_location(
                location_properties=location["properties"],
                distance=user["distance"],
            )

    return list(user_map.values())
