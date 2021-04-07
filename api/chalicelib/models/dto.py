from datetime import datetime
from typing import List, Optional

import attr
import pendulum
from pendulum.datetime import DateTime

from chalicelib.models.db import UserModel
from chalicelib.services.auth_service import generate_access_token
from chalicelib.utils import safe_parse_datetime


@attr.s(auto_attribs=True)
class LocationDTO(object):
    id: int
    url: str
    address: Optional[str]
    city: str
    state: str
    zipcode: Optional[str]
    provider: str
    last_updated: Optional[DateTime]
    distance: float

    def format_last_updated(self, user_timezone: str) -> str:
        if self.last_updated is None:
            return ""
        return self.last_updated.in_timezone(user_timezone).format("M/D/Y, h:m A zz")

    def email_context(self, user_timezone: str) -> dict:
        address_text = f"{self.address}, " if self.address else ""
        zipcode_text = f" {self.zipcode}" if self.zipcode else ""
        return {
            "title": f"{self.provider} - {address_text}{self.city}, {self.state}{zipcode_text}",
            "distance": str(round(self.distance, 1)),
            "url": self.url,
            "last_updated": self.format_last_updated(user_timezone),
            "provider": self.provider,
        }


@attr.s(auto_attribs=True)
class UserEmailDTO(object):
    email: str
    zipcode: str
    distance: str
    state_abbr: str
    timezone: str
    locations: List[LocationDTO]

    @classmethod
    def from_user(cls, user: UserModel) -> "UserEmailDTO":
        return cls(
            email=user.email,
            zipcode=user.zipcode,
            distance=str(user.distance),
            state_abbr=user.state_abbr,
            timezone=user.timezone,
            locations=[],
        )

    def add_location(self, location_properties: dict, distance: float) -> None:
        location_model = LocationDTO(
            id=location_properties["id"],
            url=location_properties["url"],
            address=location_properties["address"],
            city=location_properties["city"],
            state=location_properties["state"],
            zipcode=location_properties["postal_code"],
            provider=location_properties["provider_brand_name"],
            last_updated=safe_parse_datetime(
                location_properties["appointments_last_fetched"],
            ),
            distance=distance,
        )
        self.locations.append(location_model)

    def email_context(self) -> dict:
        return {
            "user": {
                "zipcode": self.zipcode,
                "distance": self.distance,
                "state_abbr": self.state_abbr,
                "token": generate_access_token(self.email),
            },
            "location_count": len(self.locations),
            "locations": [
                location.email_context(self.timezone)
                for location in sorted(self.locations, key=lambda i: i.distance)
            ],
        }
