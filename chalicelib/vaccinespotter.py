from typing import Optional

import requests
from requests import HTTPError

from chalicelib.logging import get_logger


logger = get_logger(__name__)


def fetch_availability_for_state(state_abbr: str) -> Optional[dict]:
    """
    Retrieves the vaccine availability for a given state
    """
    logger.info(
        "Retrieving vaccine availability for state",
        extra={"state": state_abbr},
    )
    try:
        response = requests.get(
            f"https://www.vaccinespotter.org/api/v0/states/{state_abbr}.json",
        )
    except HTTPError as e:
        logger.error(
            "Failed to process state availability",
            extra={"exception": e, "state": state_abbr},
        )
        return None

    return response.json()
