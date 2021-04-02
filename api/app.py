import os

from chalice import Chalice, Cron, ConvertToMiddleware

from chalicelib.availability import (
    compare_availability,
    fetch_state_availability_from_s3,
    update_availability_for_all_states,
)
from chalicelib.logs.utils import get_logger
from chalicelib.logs.decorators import set_request_id


app = Chalice(app_name="vaccine")
app.register_middleware(ConvertToMiddleware(set_request_id), 'all')

logger = get_logger(__name__)


@app.route("/xping")
def index():
    logger.info('Hello world')
    return {"ping": "pong"}


@app.schedule(
    Cron(f'0/{os.environ["AVAILABILITY_UPDATE_INTERVAL"]}', '*', '*', '*', '?', '*'),
    name="update-availability",
)
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
