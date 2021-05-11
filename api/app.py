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
    NotFoundError,
    Response,
)
from pydantic import ValidationError

from chalicelib import singletons
from chalicelib.logs.decorators import set_request_id
from chalicelib.logs.utils import get_logger
from chalicelib.models.api import ManagePreferences, UserSchema
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
    if valid_token:
        return valid_response
    else:
        logger.error("Invalid token")
        return invalid_response


@app.route("/xping")
def index():
    return {"ping": "pong"}


@app.route("/user", methods=["POST"], cors=True)
def handle_create_user():
    try:
        user_schema = UserSchema(**app.current_request.json_body)
    except ValidationError as e:
        logger.warning("Invalid JSON body, failed to validate schema")
        return Response(
            body=e.errors(),
            status_code=BadRequestError.STATUS_CODE,
        )

    create_new_user(user_schema)
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
        logger.warning("Invalid JSON body, failed to validate schema")
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
    return Response(body=None, status_code=204)


@app.route("/user/manage_preferences", methods=["POST"], cors=True)
def manage_preferences():
    """
    Checks for user from email property in request body
    and sends an email to containing a link to update notification
    preferences with a temp auth token included

    Returns:
        [Response]: A formatted response to the API caller
    """
    try:
        preferences_schema = ManagePreferences(**app.current_request.json_body)
    except ValidationError as e:
        logger.warning("Invalid JSON body, failed to validate schema")
        return Response(
            body=e.errors(),
            status_code=BadRequestError.STATUS_CODE,
        )

    user = fetch_user(preferences_schema.email)
    send_emails_to_users(
        [UserEmailDTO.from_user(user)],
        EmailTemplate.UpdatePreferences,
    )
    return Response(body={"message": "success"}, status_code=204)


@app.schedule(
    Cron(f'0/{os.environ["AVAILABILITY_UPDATE_INTERVAL"]}', "*", "*", "*", "?", "*"),
    name="update-availability",
)
def handle_update_availability(event):
    try:
        for states in chunk_list(us.states.STATES, 10):
            loop = get_or_create_eventloop()
            loop.run_until_complete(update_availability_for_states(states))
    except Exception as e:
        logger.error("Failed to update availability", extra={"exception": e})


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
