import time
from typing import Optional
from uuid import uuid4

from chalicelib import singletons


def ms_since_epoch(
    minutes: int = None,
    hours: int = None,
    days: int = None,
) -> int:
    future_ms = 0
    if minutes:
        future_ms += minutes * 60000
    if hours:
        future_ms += hours * 60 * 60000
    if days:
        future_ms += days * 24 * 60 * 60000

    return int(time.time() * 1000)


def str_uuid() -> str:
    return str(uuid4())
