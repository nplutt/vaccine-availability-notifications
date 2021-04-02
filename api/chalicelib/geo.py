from geopy.distance import geodesic
from chalicelib.logs.utils import get_logger
from chalicelib.logs.decorators import func_time
from typing import List
import zipcodes


logger = get_logger(__name__)


@func_time
def find_zipcode_distances(
    state_abbr: str,
    location_coordinates: List[int],
) -> dict:
    zipcode_distance_map = {
        5: [],
        10: [],
        25: [],
        50: [],
        100: [],
    }

    state_zipcodes = zipcodes.filter_by(active=True, state=state_abbr)
    for zipcode_info in state_zipcodes:
        zipcode = zipcode_info['zipcode']
        coordinates = [zipcode_info['lat'], zipcode_info['long']]

        distance = geodesic(location_coordinates, coordinates).miles
        if distance <= 5:
            zipcode_distance_map[5].append({zipcode: distance})
        if distance <= 10:
            zipcode_distance_map[10].append({zipcode: distance})
        if distance <= 25:
            zipcode_distance_map[25].append({zipcode: distance})
        if distance <= 50:
            zipcode_distance_map[50].append({zipcode: distance})
        if distance <= 100:
            zipcode_distance_map[100].append({zipcode: distance})

    return zipcode_distance_map

