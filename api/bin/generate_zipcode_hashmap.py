import zipcodes
import bz2
import us
import pygeohash
from collections import defaultdict
import json


if __name__ == '__main__':
    hashmap = defaultdict(list)
    for state in us.states.STATES:
        state_zips = zipcodes.filter_by(active=True, state=state.abbr)
        for state_zip in state_zips:
            hashmap[
                pygeohash.encode(float(state_zip['lat']), float(state_zip['long']), 3)
            ].append({
                'zip_code': state_zip['zip_code'],
                'coordinates': [state_zip["lat"], state_zip["long"]],
            })

    output = bz2.BZ2File('ziphash.json.bz2', 'wb')
    try:
        output.write(json.dumps(hashmap).encode('ascii'))
    finally:
        output.close()
