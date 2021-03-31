import json
import os
from typing import Tuple

import boto3
import us

from chalicelib.logging import get_logger
from chalicelib.vaccinespotter import fetch_availability_for_state


logger = get_logger(__name__)

s3_client = boto3.client("s3")


def update_availability_for_all_states() -> None:
    logger.info("Updating availability for all US states")
    for state in us.states.STATES:
        availability = fetch_availability_for_state(state.abbr)

        if availability is not None:
            availability = format_availability(state.abbr, availability)
            update_state_availability_in_s3(state.abbr, availability)


def format_availability(state_abbr: str, availability: dict) -> dict:
    try:
        features = availability.pop("features")
        availability["features"] = {}
        for f in features:
            availability["features"][f["id"]] = f
    except (KeyError, IndexError) as e:
        logger.error(
            "Failed to format availability",
            extra={"exception": e, "state": state_abbr},
        )

    return availability


def update_state_availability_in_s3(state_abbr: str, availability: dict) -> None:
    logger.info(
        "Uploading state availability to s3",
        extra={"state": state_abbr},
    )
    s3_client.put_object(
        Body=(bytes(json.dumps(availability).encode("UTF-8"))),
        Bucket=os.environ["VACCINE_AVAILABILITY_BUCKET"],
        Key=f"{state_abbr}/availability.json",
    )


def compare_availability(new_availability: dict, old_availability: dict) -> None:
    for location_availability in new_availability["features"]:
        location_availability_id = location_availability["id"]
        old_location_availability = old_availability["features"].get(
            location_availability_id,
        )
        if old_location_availability is None:
            logger.info(
                "Looks like a new location was added",
                extra={"id": location_availability_id},
            )
            continue

        if (
            location_availability["appointments_last_fetched"]
            == old_location_availability["appointments_last_fetched"]
        ):
            logger.info("Appointments havent been updated, skipping further processing")
            continue

        old_appointment_count = len(old_location_availability["appointments"])
        new_appointment_count = len(location_availability["appointments"])

        if old_appointment_count == 0 and new_appointment_count > 0:
            logger.info("Whoo there are new appointments available!!!")


def fetch_state_availability_from_s3(key: str) -> Tuple[dict, dict]:
    object_versions = s3_client.list_object_versions(
        Bucket=os.environ["VACCINE_AVAILABILITY_BUCKET"],
        Prefix=key,
        MaxKeys=2,
    )
    object_version_ids = [v["VersionId"] for v in object_versions["Versions"]]

    old_state_availability = s3_client.get_object(
        Bucket=os.environ["VACCINE_AVAILABILITY_BUCKET"],
        Key=key,
        VersionId=object_version_ids[1],
    )
    new_state_availability = s3_client.get_object(
        Bucket=os.environ["VACCINE_AVAILABILITY_BUCKET"],
        Key=key,
        VersionId=object_version_ids[0],
    )
    return (
        json.loads(new_state_availability["Body"].read().decode("utf-8")),
        json.loads(old_state_availability["Body"].read().decode("utf-8")),
    )
