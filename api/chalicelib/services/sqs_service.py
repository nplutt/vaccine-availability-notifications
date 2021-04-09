import json
import os
from typing import List

import boto3

from chalicelib.logs.utils import get_logger
from chalicelib.utils import chunk_list


logger = get_logger(__name__)

sqs_client = boto3.client("sqs")


def send_location_availability_to_queue(locations: List[dict]) -> None:
    for chunk in chunk_list(locations, 10):
        try:
            sqs_client.send_message(
                QueueUrl=os.environ["LOCATION_AVAILABILITY_QUEUE_URL"],
                MessageBody=json.dumps(chunk),
            )
        except Exception as e:
            logger.error(
                "Failed to send locations to availability queue",
                extra={
                    "error": e,
                    "chunk": chunk,
                },
            )
