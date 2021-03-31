import os

from chalice import Chalice, Rate

from chalicelib.availability import (
    compare_availability,
    fetch_state_availability_from_s3,
    update_availability_for_all_states,
)
from chalicelib.logging import get_logger


app = Chalice(app_name="vaccine")

logger = get_logger(__name__)


@app.route("/")
def index():
    return {"ping": "pong"}


@app.schedule(Rate(5, unit=Rate.MINUTES), name="update-availability")
def update_availability(event):
    update_availability_for_all_states()


@app.on_s3_event(
    os.environ["VACCINE_AVAILABILITY_BUCKET"],
    events=["s3:ObjectCreated:*"],
    name="diff-availability",
)
def diff_availability(event):
    logger.info(
        "Updating availability for state",
        extra={"state": event.key},
    )
    new_availability, old_availability = fetch_state_availability_from_s3(event.key)
    compare_availability(new_availability, old_availability)
