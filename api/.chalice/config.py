import boto3
import os
import json


def main():
    account_id = boto3.client('sts').get_caller_identity().get('Account')

    file_path = '{}/.chalice/config.json'.format(os.getcwd())
    config = {
        "version": "2.0",
        "app_name": "vaccine",
        "autogen_policy": False,
        "environment_variables": {
            "AVAILABILITY_UPDATE_INTERVAL": "2",
            "REGION": "us-west-2",
            "LOG_LEVEL": "INFO",
        },
        "iam_policy_file": "policy.json",
        "lambda_memory_size": 512,
        "lambda_timeout": 60,
        "stages": {
            "prod": {
                "api_gateway_stage": "api",
                "environment_variables": {
                    "DYNAMO_DB_TABLE_NAME": "user-vaccine-notifications-prod",
                    "LOCATION_AVAILABILITY_QUEUE_NAME": "vaccine-reminders-location-availability-prod",
                    "LOCATION_AVAILABILITY_QUEUE_URL": f"https://sqs.us-west-2.amazonaws.com/{account_id}/vaccine-reminders-location-availability-prod",
                    "VACCINE_AVAILABILITY_BUCKET": "nplutt-prod-vaccine-reminders-data"
                },
                "lambda_functions": {
                    "diff-availability": {
                        "lambda_timeout": 60,
                        "lambda_memory_size": 512
                    },
                    "process-location-availability": {
                        "lambda_timeout": 180,
                        "lambda_memory_size": 1024
                    },
                },
                "tags": {"Environment": "prod"}
            }
        },
        "tags": {
            "Name": "vaccine-availability",
            "Project": "vaccine-availability"
        }
    }

    with open(file_path, 'w') as fp:
        fp.write(json.dumps(config, indent=4))


if __name__ == '__main__':
    main()
