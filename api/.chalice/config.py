import json
import os

import boto3


ssm_client = boto3.client("ssm")
sts_client = boto3.client("sts")


def main():
    account_id = sts_client.get_caller_identity()["Account"]
    jwt_secret = ssm_client.get_parameter(
        Name="/vaccine-reminders/prod/JWT_SECRET",
        WithDecryption=True,
    )["Parameter"]["Value"]

    file_path = "{}/.chalice/config.json".format(os.getcwd())
    config = {
        "version": "2.0",
        "app_name": "vaccine",
        "autogen_policy": False,
        "environment_variables": {
            "AVAILABILITY_UPDATE_INTERVAL": "3",
            "REGION": "us-west-2",
            "LOG_LEVEL": "INFO",
            "DYNAMO_DB_TABLE_NAME": "user-vaccine-notifications-prod",
            "JWT_SECRET": jwt_secret,
            "LOCATION_AVAILABILITY_QUEUE_NAME": "vaccine-reminders-location-availability-prod",
            "LOCATION_AVAILABILITY_QUEUE_URL": f"https://sqs.us-west-2.amazonaws.com/{account_id}/vaccine-reminders-location-availability-prod",
            "SEND_EMAILS": "TRUE",
            "SES_EMAIL_TEMPLATE": "vaccine-reminders-basic-template",
            "SES_REPLY_TO_ADDRESS": "Vaccine Notifications <notifications@covid-vaccine-notifications.org>",
            "VACCINE_AVAILABILITY_BUCKET": "nplutt-prod-vaccine-reminders-data",
        },
        "iam_policy_file": "policy.json",
        "lambda_memory_size": 512,
        "lambda_timeout": 60,
        "stages": {
            "prod": {
                "api_gateway_stage": "api",
                "lambda_functions": {
                    "diff-availability": {
                        "lambda_timeout": 60,
                        "lambda_memory_size": 512,
                    },
                    "process-location-availability": {
                        "lambda_timeout": 180,
                        "lambda_memory_size": 1024,
                    },
                },
                "tags": {"Environment": "prod"},
            },
        },
        "tags": {"Name": "vaccine-availability", "Project": "vaccine-availability"},
    }

    with open(file_path, "w") as fp:
        fp.write(json.dumps(config, indent=4))


if __name__ == "__main__":
    main()
