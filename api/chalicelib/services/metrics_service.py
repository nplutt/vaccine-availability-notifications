import os

import boto3


cloudwatch_client = boto3.client("cloudwatch")


def send_user_created_metric() -> None:
    cloudwatch_client.put_metric_data(
        Namespace=os.environ["METRIC_NAMESPACE"],
        MetricData=[
            {
                "MetricName": "user_event",
                "Dimensions": [
                    {
                        "Name": "type",
                        "Value": "created",
                    },
                ],
                "Value": 1,
                "Unit": "Count",
            },
        ],
    )


def send_user_deleted_metric() -> None:
    cloudwatch_client.put_metric_data(
        Namespace=os.environ["METRIC_NAMESPACE"],
        MetricData=[
            {
                "MetricName": "user_event",
                "Dimensions": [
                    {
                        "Name": "type",
                        "Value": "deleted",
                    },
                ],
                "Value": 1,
                "Unit": "Count",
            },
        ],
    )
