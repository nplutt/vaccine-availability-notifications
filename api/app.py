import os

from chalice import (
    AuthResponse,
    Chalice,
    ConvertToMiddleware,
    Cron,
    ForbiddenError,
    Response,
)

from chalicelib import singletons
from chalicelib.logs.decorators import set_request_id
from chalicelib.logs.utils import get_logger
from chalicelib.models.api import UserSchema
from chalicelib.services.auth_service import access_token_valid, get_user_id
from chalicelib.services.availability_service import (
    compare_availability,
    fetch_state_availability_from_s3,
    update_availability_for_all_states,
)
from chalicelib.services.user_service import create_new_user
from chalicelib.services.email_service import notify_users


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


@app.route("/notify_users", methods=["POST"])
def handle_notify_users():
    if app.current_request.method == "POST":
        notify_users(app.current_request.json_body)


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
