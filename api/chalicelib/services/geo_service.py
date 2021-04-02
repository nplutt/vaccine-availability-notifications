from typing import Dict, List

import zipcodes
from geopy.distance import geodesic

from chalicelib.logs.decorators import func_time
from chalicelib.logs.utils import get_logger
from collections import defaultdict

logger = get_logger(__name__)


@func_time
def find_zipcode_distances(
    state_abbr: str,
    location_coordinates: List[int],
) -> dict:
    zipcode_distance_map: Dict[int, Dict[str, int]] = defaultdict(dict)

    state_zipcodes = zipcodes.filter_by(active=True, state=state_abbr)
    for zipcode_info in state_zipcodes:
        zipcode = zipcode_info["zipcode"]
        coordinates = [zipcode_info["lat"], zipcode_info["long"]]

        distance = geodesic(location_coordinates, coordinates).miles
        if distance <= 5:
            zipcode_distance_map[5][zipcode] = distance
        if distance <= 10:
            zipcode_distance_map[10][zipcode] = distance
        if distance <= 25:
            zipcode_distance_map[25][zipcode] = distance
        if distance <= 50:
            zipcode_distance_map[50][zipcode] = distance
        if distance <= 100:
            zipcode_distance_map[100][zipcode] = distance

    return zipcode_distance_map
