import json
import os
from time import sleep
from typing import List

import boto3

from chalicelib.logs.decorators import func_time
from chalicelib.logs.utils import get_logger
from chalicelib.models.dto import UserEmailDTO
from chalicelib.services.template_service import render_template
from chalicelib.utils import chunk_list


logger = get_logger(__name__)

ses_client = boto3.client("ses")


@func_time
def send_new_appointment_emails_to_users(users: List[UserEmailDTO]) -> None:
    for chunk in chunk_list(users, 50):
        ses_client.send_bulk_templated_email(
            Source=os.environ["SES_REPLY_TO_ADDRESS"],
            Template=os.environ["SES_EMAIL_TEMPLATE"],
            DefaultTemplateData=json.dumps({}),
            Destinations=[
                {
                    "Destination": {
                        "ToAddresses": [u.email],
                    },
                    "ReplacementTemplateData": json.dumps(
                        {
                            "subject": "New vaccine appointments near you!",
                            "html": render_template(
                                "./chalicelib/templates/new_appointments.html",
                                u.email_context(),
                            ),
                            "text": render_template(
                                "./chalicelib/templates/new_appointments.txt",
                                u.email_context(),
                            ),
                        },
                    ),
                }
                for u in chunk
            ],
        )
