from chalicelib.logs.utils import get_logger
from chalicelib.repositories.user_repository import (
    load_users_by_parent_geohash_distance,
)
from chalicelib.services.geo_service import find_zipcode_distances, find_geohashes_in_radius
from chalicelib.logs.decorators import func_time


logger = get_logger(__name__)


@func_time
def notify_users(location: dict) -> None:
    state_abbr = location["properties"]["state"]
    coordinates = location["geometry"]["coordinates"]
    coordinates.reverse()

    zipcode_distances = find_zipcode_distances(
        state_abbr=state_abbr,
        location_coordinates=coordinates,
    )

    for distance, zipcodes in zipcode_distances.items():
        zipcode_set = set(zipcodes.keys())
        parent_geohashes = find_geohashes_in_radius(coordinates[0], coordinates[1], distance)

        users = []
        for geohash in parent_geohashes:
            unfiltered_users = load_users_by_parent_geohash_distance(geohash, distance)
            users = users + list(filter(lambda u: u.zipcode in zipcode_set, unfiltered_users))

        logger.info('Retrieved users from DynamoDB', extra={
            'users': len(users),
            'zipcodes': len(zipcode_set),
            'distance': distance,
        })
