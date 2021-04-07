import asyncio
import time
from typing import Any, List, Optional, Union
from uuid import uuid4

from pendulum import Date, DateTime, Duration, Time, parse


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


def chunk_list(lst: List[Any], n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def safe_parse_datetime(date_time: Optional[str]) -> Optional[DateTime]:
    if date_time is not None and len(date_time) > 0:
        try:
            return parse(date_time)  # type: ignore
        except Exception:
            pass
    return None


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
