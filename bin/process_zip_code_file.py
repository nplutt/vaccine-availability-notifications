import json


if __name__ == "__main__":
    # Data set downloaded from
    # https://public.opendatasoft.com/explore/dataset/us-zip-code-latitude-and-longitude/export/
    zip_code_map = {}

    with open("/Users/nplutt/Downloads/us-zip-code-latitude-and-longitude.json") as f:
        records = json.load(f)

    for record in records:
        fields = record["fields"]
        zip_code_map[fields["zip"]] = (fields["latitude"], fields["longitude"])

    zip_code_file = open("./chalicelib/static/zipcode_coordinates.py", "w")
    zip_code_file.write(
        f"zipcode_coordinate_map = {json.dumps(zip_code_map, indent=4)}",
    )
    zip_code_file.close()
