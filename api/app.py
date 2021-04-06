import os

from chalice import AuthResponse, Chalice, ConvertToMiddleware, Cron, Response

from chalicelib import singletons
from chalicelib.logs.decorators import set_request_id
from chalicelib.logs.utils import get_logger
from chalicelib.models.api import UserSchema
from chalicelib.services.auth_service import access_token_valid
from chalicelib.services.availability_service import (
    compare_availability,
    fetch_state_availability_from_s3,
    update_availability_for_all_states,
)
from chalicelib.services.user_service import create_new_user, find_users_to_notify_for_location, bulk_notify_users
from chalicelib.utils import get_or_create_eventloop
import json


app = Chalice(app_name="vaccine")
app.debug = True
app.register_middleware(ConvertToMiddleware(set_request_id), "all")
singletons.app = app

logger = get_logger(__name__)


@app.authorizer(name="internal-authorizer")
def internal_authorizer(auth_request):
    invalid_response = AuthResponse(routes=[], principal_id="user")
    valid_response = AuthResponse(routes=["/*"], principal_id="user")
    valid_token, _ = access_token_valid(auth_request.token)
    return valid_response if valid_token else invalid_response


@app.route("/xping")
def index():
    return {"ping": "pong"}


@app.route("/v1/notify_users", methods=["POST"])
def handle_notify_users_1():
    if app.current_request.method == "POST":
        find_users_to_notify_for_location(app.current_request.json_body)


@app.route("/v2/notify_users", methods=["POST"])
def handle_notify_users_2():
    if app.current_request.method == "POST":
        loop = get_or_create_eventloop()
        loop.run_until_complete(bulk_notify_users(app.current_request.json_body))


@app.route("/user", methods=["POST"])
def handle_create_user():
    if app.current_request.method == "POST":
        user_schema = UserSchema(**app.current_request.json_body)
        create_new_user(user_schema)
        return Response(body=None, status_code=201)


@app.route("/user", methods=["GET", "PATCH"], authorizer=internal_authorizer)
def handle_get_user():
    if app.current_request.method == "GET":
        pass
    elif app.current_request.method == "PATCH":
        pass


@app.schedule(
    Cron(f'0/{os.environ["AVAILABILITY_UPDATE_INTERVAL"]}', "*", "*", "*", "?", "*"),
    name="update-availability",
)
def handle_update_availability(event):
    update_availability_for_all_states()


@app.on_s3_event(
    os.environ["VACCINE_AVAILABILITY_BUCKET"],
    events=["s3:ObjectCreated:*"],
    name="diff-availability",
)
def handle_diff_availability(event):
    logger.info(
        "Updating availability for state",
        extra={"state": event.key},
    )
    new_availability, old_availability = fetch_state_availability_from_s3(event.key)
    compare_availability(new_availability, old_availability)


@app.on_sqs_message(
    queue=os.environ['LOCATION_AVAILABILITY_QUEUE_NAME'],
    name='process-location-availability',
)
def handle_process_location_availability(event):
    for record in event:
        locations = json.loads(record.body)
        loop = get_or_create_eventloop()
        loop.run_until_complete(bulk_notify_users(locations))
