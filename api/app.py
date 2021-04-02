import os

from chalice import Chalice, ConvertToMiddleware, Cron, AuthResponse, Response

from chalicelib.services.availability import (
    compare_availability,
    fetch_state_availability_from_s3,
    update_availability_for_all_states,
)
from chalicelib.logs.decorators import set_request_id
from chalicelib.logs.utils import get_logger
from chalicelib.services.auth import access_token_valid
from chalicelib import singletons
from chalicelib.models.api import UserSchema

app = Chalice(app_name="vaccine")
app.register_middleware(ConvertToMiddleware(set_request_id), "all")
singletons.app = app

logger = get_logger(__name__)


@app.authorizer(name='internal-authorizer')
def internal_authorizer(auth_request):
    invalid_response = AuthResponse(routes=[], principal_id='user')
    valid_response = AuthResponse(routes=['/*'], principal_id='user')
    valid_token, _ = access_token_valid(auth_request.token)
    return valid_response if valid_token else invalid_response


@app.route("/xping")
def index():
    return {"ping": "pong"}


@app.route("/user", methods=['POST'])
def handle_create_user():
    if app.current_request.method == 'POST':
        user = UserSchema(**app.current_request.json_body)
        # Create user
        return Response(
            body=None,
            status_code=201,
            headers={'Location': f"/users/{user}"}
        )


@app.route("/users/{user_id}", methods=['GET', 'PATCH'], authorizer=internal_authorizer)
def handle_create_user(user_id):
    if app.current_request.method == 'GET':
        pass
    elif app.current_request.method == 'PATCH':
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
