import time
from uuid import uuid4


def ms_since_epoch() -> int:
    return int(time.time() * 1000)


def str_uuid() -> str:
    return str(uuid4())
