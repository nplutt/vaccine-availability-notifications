import asyncio
from typing import List

from chalicelib.logs.decorators import func_time
from chalicelib.logs.utils import get_logger
from chalicelib.repositories.user_repository import (
    load_users_by_parent_geohash_distance,
)
from chalicelib.services.geo_service import (
    find_geohashes_in_radius,
    find_zipcode_distances,
    find_zipcodes_in_radius,
)
from chalicelib.utils import get_or_create_eventloop


logger = get_logger(__name__)


@func_time
def notify_users(location: dict) -> None:
    state_abbr = location["properties"]["state"]
    coordinates = location["geometry"]["coordinates"]
    coordinates.reverse()

    find_zipcode_distances(
        state_abbr=state_abbr,
        location_coordinates=coordinates,
    )

    for distance in [5, 10, 25, 50]:
        try:
            parent_geohashes = find_geohashes_in_radius(
                coordinates[0], coordinates[1], distance,
            )
        except TypeError as e:
            logger.error(
                "Failed to find geohashes in radius",
                extra={
                    "coordinates": coordinates,
                    "error": e,
                },
            )
            continue

        zipcode_distances = find_zipcodes_in_radius(parent_geohashes, coordinates, distance)
        zipcode_set = set(zipcode_distances.keys())

        users = []
        filtered_user_count = 0
        for geohash in parent_geohashes:
            unfiltered_users = load_users_by_parent_geohash_distance(geohash, distance)
            filtered_users = list(
                filter(lambda u: u.zipcode in zipcode_set, unfiltered_users),
            )
            filtered_user_count = len(unfiltered_users) - len(filtered_users)
            users = users + filtered_users

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
        loop.run_in_executor(None, notify_users, location) for location in locations
    ]
    for res in await asyncio.gather(*futures):
        pass
