import json
import os
from enum import Enum
from typing import List

import attr
import boto3

from chalicelib.logs.decorators import func_time
from chalicelib.logs.utils import get_logger
from chalicelib.models.dto import UserEmailDTO
from chalicelib.services.template_service import render_template
from chalicelib.utils import chunk_list


logger = get_logger(__name__)

ses_client = boto3.client("ses")


@attr.s(auto_attribs=True)
class Email:
    subject: str
    template_name: str


class EmailTemplate(Enum):
    NewAppointments = Email(
        subject="New vaccine appointments near you!",
        template_name="new_appointments",
    )
    WELCOME = Email(subject="Welcome!", template_name="welcome")
    UpdatePreferences = Email(
        subject="Update your email preferences",
        template_name="update_preferences"
    )

    @property
    def subject(self) -> str:
        return self.value.subject

    @property
    def template_name(self) -> str:
        return self.value.template_name


@func_time
def send_emails_to_users(
    users: List[UserEmailDTO],
    email_template: EmailTemplate,
) -> None:
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
                            "subject": f"{email_template.subject}",
                            "html": render_template(
                                f"./chalicelib/templates/{email_template.template_name}.html",
                                u.email_context(),
                            ),
                            "text": render_template(
                                f"./chalicelib/templates/{email_template.template_name}.txt",
                                u.email_context(),
                            ),
                        },
                    ),
                }
                for u in chunk
            ],
        )
