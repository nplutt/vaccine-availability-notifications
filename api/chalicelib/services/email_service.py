import json
import os
from typing import List

import boto3

from chalicelib.logs.decorators import func_time
from chalicelib.logs.utils import get_logger
from chalicelib.models.dto import UserEmailDTO
from chalicelib.services.template_service import render_template
from chalicelib.utils import chunk_list
from chalicelib.enums.EmailTemplate import EmailTemplate


logger = get_logger(__name__)

ses_client = boto3.client("ses")


@func_time
def send_emails_to_users(users: List[UserEmailDTO], template: EmailTemplate) -> None:
    if os.environ.get("SEND_EMAILS") != "TRUE":
        return None

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
                                f"./chalicelib/templates/{template.value}.html",
                                u.email_context(),
                            ),
                            "text": render_template(
                                f"./chalicelib/templates/{template.value}.txt",
                                u.email_context(),
                            ),
                        },
                    ),
                }
                for u in chunk
            ],
        )
