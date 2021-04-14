import json
import os
from typing import List

import us
from chalice import (
    AuthResponse,
    BadRequestError,
    Chalice,
    ConvertToMiddleware,
    Cron,
    Response,
)
from pydantic import ValidationError

from chalicelib import singletons
from chalicelib.logs.decorators import set_request_id
from chalicelib.logs.utils import get_logger
from chalicelib.models.api import UserSchema
from chalicelib.models.dto import UserEmailDTO
from chalicelib.services.auth_service import access_token_valid, get_user_email
from chalicelib.services.availability_service import (
    compare_availability,
    fetch_state_availability_from_s3,
    update_availability_for_states,
)
from chalicelib.services.email_service import (
    EmailTemplate,
    send_emails_to_users,
)
from chalicelib.services.metrics_service import (
    send_user_created_metric,
    send_user_deleted_metric,
)
from chalicelib.services.user_service import (
    create_new_user,
    delete_user,
    fetch_user,
    find_users_to_notify_for_locations,
    update_user,
)
from chalicelib.utils import chunk_list, get_or_create_eventloop


app = Chalice(app_name="vaccine")
app.debug = True
app.register_middleware(ConvertToMiddleware(set_request_id), "all")
singletons.app = app

logger = get_logger(__name__)


@app.authorizer(name="internal-authorizer")
def internal_authorizer(auth_request):
    invalid_response = AuthResponse(routes=[], principal_id="user")
    valid_response = AuthResponse(routes=["/*"], principal_id="user")

    try:
        authorization_header = auth_request.token
        bearer_token = authorization_header.split(" ")[1]
    except IndexError:
        return invalid_response

    valid_token, _ = access_token_valid(bearer_token)
    return valid_response if valid_token else invalid_response


@app.route("/xping")
def index():
    return {"ping": "pong"}


@app.route("/user", methods=["POST"], cors=True)
def handle_create_user():
    try:
        user_schema = UserSchema(**app.current_request.json_body)
    except ValidationError as e:
        return Response(
            body=e.errors(),
            status_code=BadRequestError.STATUS_CODE,
        )

    create_new_user(user_schema)
    send_user_created_metric()
    return Response(body=None, status_code=201)


@app.route("/user", methods=["GET"], authorizer=internal_authorizer, cors=True)
def handle_get_user():
    user = fetch_user(get_user_email())
    return {
        "email": user.email,
        "zipcode": user.zipcode,
        "distance": user.distance,
    }


@app.route("/user", methods=["PATCH"], authorizer=internal_authorizer, cors=True)
def handle_update_user():
    try:
        user_schema = UserSchema(**app.current_request.json_body)
    except ValidationError as e:
        return Response(
            body=e.errors(),
            status_code=BadRequestError.STATUS_CODE,
        )

    user = fetch_user(get_user_email())
    update_user(user_schema, user)
    return Response(body=None, status_code=204)


@app.route("/user", methods=["DELETE"], authorizer=internal_authorizer, cors=True)
def handle_delete_user():
    user = fetch_user(get_user_email())
    delete_user(user)
    send_user_deleted_metric()
    return Response(body=None, status_code=204)


@app.schedule(
    Cron(f'0/{os.environ["AVAILABILITY_UPDATE_INTERVAL"]}', "*", "*", "*", "?", "*"),
    name="update-availability",
)
def handle_update_availability(event):
    for states in chunk_list(us.states.STATES, 10):
        loop = get_or_create_eventloop()
        loop.run_until_complete(update_availability_for_states(states))


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
    queue=os.environ["LOCATION_AVAILABILITY_QUEUE_NAME"],
    name="process-location-availability",
)
def handle_process_location_availability(event):
    for record in event:
        locations = json.loads(record.body)
        loop = get_or_create_eventloop()
        users: List[UserEmailDTO] = loop.run_until_complete(
            find_users_to_notify_for_locations(locations),
        )
        send_emails_to_users(users, EmailTemplate.NewAppointments)
