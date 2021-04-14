import asyncio
import json
import os
from typing import Any, List, Tuple

import boto3

from chalicelib.logs.utils import get_logger
from chalicelib.services.sqs_service import send_location_availability_to_queue
from chalicelib.services.vaccinespotter_service import (
    fetch_availability_for_state,
)
from chalicelib.utils import get_or_create_eventloop


logger = get_logger(__name__)

s3_client = boto3.client("s3")


async def update_availability_for_states(states: List[Any]) -> None:
    logger.info(
        "Updating availability for states",
        extra={
            "count": len(states),
        },
    )
    loop = get_or_create_eventloop()
    futures = [
        loop.run_in_executor(None, update_availability_for_state, state.abbr)
        for state in states
    ]
    await asyncio.gather(*futures)


def update_availability_for_state(state_abbr: str) -> None:
    availability = fetch_availability_for_state(state_abbr)

    if availability is not None:
        availability = format_availability(state_abbr, availability)
        update_state_availability_in_s3(state_abbr, availability)


def format_availability(state_abbr: str, availability: dict) -> dict:
    try:
        features = availability.pop("features")
        availability["features"] = {}
        for f in features:
            feature_id = f["properties"]["id"]
            availability["features"][feature_id] = f
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


def compare_availability(new_availability: dict, old_availability: dict) -> None:
    locations = []
    for location_id, location_availability in new_availability["features"].items():
        old_location_availability = old_availability["features"].get(location_id)
        if old_location_availability is None:
            continue

        if (
            location_availability["properties"]["appointments_last_fetched"]
            == old_location_availability["properties"]["appointments_last_fetched"]
        ):
            # Appointments haven't been updated, skipping further processing
            continue

        old_appointment_count = _get_location_appointment_count(
            old_location_availability,
        )
        new_appointment_count = _get_location_appointment_count(location_availability)

        if old_appointment_count == 0 and new_appointment_count > 0:
            # New appointments available but lets pop off the appointments info
            # to save room in SQS
            location_availability["properties"].pop("appointments")
            locations.append(location_availability)

    logger.info("Locations with new appointments", extra={"count": len(locations)})
    send_location_availability_to_queue(locations)


def _get_location_appointment_count(location: dict) -> int:
    appointments = location["properties"]["appointments"]
    if appointments is None:
        logger.info(
            "Appointments value is null",
            extra={"provider": location["properties"]["provider"]},
        )
        return 0
    else:
        return len(appointments)
