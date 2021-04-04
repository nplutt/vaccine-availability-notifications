import logging
import os
from typing import Optional
from uuid import uuid4

from pythonjsonlogger import jsonlogger


def get_logger(name):
    logger = logging.getLogger(name)

    formatter = CustomJsonFormatter()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
    logger.propagate = False

    return logger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["request_id"] = CURRENT_REQUEST_ID.get_request_id()


class CurrentRequestId(object):
    def __init__(self):
        self.current_request_id: str = str(uuid4())

    def set_request_id(self, request_id: Optional[str]) -> None:
        if not request_id:
            request_id = str(uuid4())
        self.current_request_id = request_id

    def get_request_id(self) -> str:
        return self.current_request_id


CURRENT_REQUEST_ID = CurrentRequestId()
