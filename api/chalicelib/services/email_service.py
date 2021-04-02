from chalicelib.services.geo_service import find_zipcode_distances
from chalicelib.repositories.user_repository import batch_get_users_by_zipcode_distance


def notify_users(location: dict) -> None:
    state_abbr = location['properties']['state']
    coordinates = location['geometry']['coordinates'].reverse()
    zipcode_distances = find_zipcode_distances(
        state_abbr=state_abbr,
        location_coordinates=coordinates,
    )

    for distance, zipcodes in zipcode_distances.items():
        users = batch_get_users_by_zipcode_distance(zipcodes.keys(), str(distance))
        logger.
