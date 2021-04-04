import os
from typing import Optional, Tuple

import jwt
from jwt import PyJWTError

from chalicelib import singletons
from chalicelib.utils import ms_since_epoch


def generate_access_token(user_id: str, user_email: str) -> str:
    """
    Generates a JWT token for a given user that is valid for n number of days
    """
    payload = {
        "user_id": user_id,
        "email": user_email,
        "exp": ms_since_epoch(days=90),
    }
    return jwt.encode(
        payload=payload,
        key=os.environ["JWT_SECRET"],
        algorithm="HS256",
    ).decode("utf-8")


def access_token_valid(token: str) -> Tuple[bool, Optional[str]]:
    """
    Checks that the access token is valid
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=os.environ["JWT_SECRET"],
            algorithms=["HS256"],
        )
    except PyJWTError:
        return False, None

    return payload["exp"] < ms_since_epoch(), payload["user_id"]


def get_user_id() -> Optional[str]:
    token = singletons.app.current_request.headers.get("Authorization").split(" ")[1]
    _, user_id = access_token_valid(token)
    return user_id
