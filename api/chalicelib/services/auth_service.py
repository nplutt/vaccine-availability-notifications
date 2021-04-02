import jwt
from jwt import PyJWTError
from chalicelib.utils import ms_since_epoch
import os
from typing import Tuple, Optional
from chalicelib import singletons


def generate_access_token(user_email: str) -> str:
    """
    Generates a JWT token for a given user that is valid for n number of days
    """
    payload = {
        'email': user_email,
        'exp': ms_since_epoch(days=90),
    }
    return jwt.encode(
        payload=payload,
        key=os.environ['JWT_SECRET'],
        algorithm='HS256',
    ).decode('utf-8')


def access_token_valid(token: str) -> Tuple[bool, Optional[str]]:
    """
    Checks that the access token is valid
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=os.environ['JWT_SECRET'],
            algorithms=['HS256'],
        )
    except PyJWTError:
        return False, None

    return payload['exp'] < ms_since_epoch(), payload['email']


def get_user_email() -> Optional[str]:
    token = singletons.app.current_request.headers.get('Authorization').split(' ')[1]
    _, user_email = access_token_valid(token)
    return user_email
