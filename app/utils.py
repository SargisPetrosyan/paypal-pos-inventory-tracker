from datetime import datetime, timedelta
import os
import json
import logging
from uuid import UUID
from dataclasses import dataclass, field

from fastapi import Request
import httpx
import pytz


from app.constants import (
    PAYPAL_AUTH_URL,
    PAYPAL_GRANT_TYPE,
    PAYPAL_HEADERS,
    UTC_TIMEZONE_NAME,
)

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class PaypalTokenData:
    shop_name: str
    _access_key: str | None = None

    def __post_init__(self):
        if self._access_key is None:
            self.access_key = self._get_access_key()

    @property
    def access_key(self) -> str:
        if not  self._access_key:
            raise(TypeError("access ky doesn't have value"))
        return self._access_key
    
    @access_key.setter
    def access_key(self, access_key:str):
        self._access_key = access_key

    def _get_access_key(self) -> str:

        headers: dict[str, str] = {"Content-Type": PAYPAL_HEADERS}
        url: str = PAYPAL_AUTH_URL

        data: dict[str, str] = {
            "grant_type": PAYPAL_GRANT_TYPE,
            "client_id": os.environ[f"{self.shop_name.upper()}_CLIENT_ID"],
            "assertion": os.environ[f"{self.shop_name.upper()}_KEY"],
        }

        response = httpx.post(url=url, data=data, headers=headers)
        response.raise_for_status()

        formatted_data = response.json()

        self.expiration_date = os.environ[
            f"{self.shop_name.upper()}_ACCESS_KEY_EXPIATION_DATE"
        ] = str(datetime.now() + timedelta(seconds=formatted_data["expires_in"]))

        return formatted_data["access_token"]


async def json_to_dict(request: Request) -> dict:
    body: bytes = await request.body()
    data = json.loads(body)
    payload = data.get("payload")
    if isinstance(payload, str):
        try:
            data["payload"] = json.loads(payload)
        except json.JSONDecodeError:
            logger.warning(
                "Webhook payload is string but contains invalid JSON. Keeping raw string payload."
            )
            data["payload"] = payload
    else:
        data["payload"] = payload
    return data

def any_to_utc(date: datetime) -> datetime:
    """convert any timezone datetime to utc"""
    utc: datetime = date.astimezone(pytz.timezone(UTC_TIMEZONE_NAME))
    return utc


@dataclass
class CredentialContext:
    shop_name: str
    mail: str = os.environ["MAIL"]
    events: list[str] = field(default_factory=list[str])
    subscription_uuid: str = field(init=False)
    destination_url: str = field(init=False)

    def __post_init__(self):
        self.subscription_uuid: str = os.environ[
            f"{self.shop_name.upper()}_SUBSCRIPTION_UUID"
        ]
        self.destination_url: str = (
            os.environ["DESTINATION_URL"] + "/inventory_tracker_webhook"
        )


class ShopInfo:
    def __init__(self) -> None:
        self.dict = {
            UUID(os.environ["DALA_ORGANIZATION_UUID"]): "DALA_SHOP",
            UUID(os.environ["ART_ORGANIZATION_UUID"]): "ART_CRAFT",
            UUID(os.environ["CAFE_ORGANIZATION_UUID"]): "CAFE",
        }

    def get_shop_name_by_id(self, shop_id: UUID):
        return self.dict[shop_id]

def webhook_request(response: dict) -> bool:
    if response["eventName"] == "TestMessage":
        return True
    return False
