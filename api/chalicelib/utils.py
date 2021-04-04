import asyncio
import time
from uuid import uuid4


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


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
