from datetime import  datetime, timedelta
import json
import logging
from uuid import UUID
from fastapi import Request
import httpx
from azure.servicebus import ServiceBusClient
import os
import pytz
from datetime import datetime
from dataclasses import dataclass,field

from sqlalchemy import Engine
from sqlmodel import Session

from app.constants import PAYPAL_AUTH_URL, PAYPAL_GRANT_TYPE, PAYPAL_HEADERS, SHOP_SUBSCRIPTION_EVENTS, SWEDEN_TIMEZONE_NAME
from app.db.schemes import InventoryBalanceUpdateRepository
from app.models.inventory import InventoryBalanceUpdateValidator

logger: logging.Logger = logging.getLogger(name=__name__)
import os

logger: logging.Logger = logging.getLogger(name=__name__)

@dataclass
class PaypalTokenData:
    shop_name: str
    access_key: str | None = None

    def __post_init__(self):
        if self.access_key is None:
            self.access_key = self._get_access_key()

    def _get_access_key(self)-> str:

        headers: dict[str, str] = {"Content-Type": PAYPAL_HEADERS}
        url: str = PAYPAL_AUTH_URL

        data: dict[str, str] = {
            "grant_type": PAYPAL_GRANT_TYPE,
            "client_id": os.environ[f"{ self.shop_name.upper()}_CLIENT_ID"],
            "assertion": os.environ[f"{ self.shop_name.upper()}_KEY"],
        }

        response = httpx.post(url=url, data=data, headers=headers)
        response.raise_for_status()

        formatted_data = response.json()

        self.expiration_date = os.environ[f"{ self.shop_name.upper()}_ACCESS_KEY_EXPIATION_DATE"] = str(datetime.now() + timedelta(
            seconds=formatted_data["expires_in"]
        ))

        return formatted_data['access_token']

async def json_to_dict(request:Request)-> dict:
    body: bytes = await request.body()
    data = json.loads(body)
    payload = data.get("payload")
    if isinstance(payload, str):
        try:
            data["payload"] = json.loads(payload)
        except json.JSONDecodeError:
            logger.warning("Webhook payload is string but contains invalid JSON. Keeping raw string payload.")
            data["payload"] = payload
    else:
        data["payload"] = payload
    return data

def any_to_cet(date:datetime) -> datetime:
    SWEDEN_TIMEZONE: datetime = date.astimezone(pytz.timezone(SWEDEN_TIMEZONE_NAME))
    return SWEDEN_TIMEZONE

@dataclass
class CredentialContext():
    shop_name: str
    mail: str = os.environ["MAIL"]
    events: list[str] = SHOP_SUBSCRIPTION_EVENTS
    subscription_uuid: str = field(init=False)
    destination_url: str = field(init=False)

    def __post_init__(self):
        self.subscription_uuid: str  = os.environ[f"{self.shop_name.upper()}_SUBSCRIPTION_UUID"]
        self.destination_url: str  = os.environ["DESTINATION_URL"] + "/inventory_tracker_webhook"

class ShopInfo:
    def __init__(self) -> None:
        self.dict = {
            UUID(os.environ['DALA_ORGANIZATION_UUID']): 'DALA_SHOP',
            UUID(os.environ['ART_ORGANIZATION_UUID']): 'ART_CRAFT',
            UUID(os.environ['CAFE_ORGANIZATION_UUID']): 'CAFE',
        }
    def get_shop_name_by_id(self,shop_id:UUID):
        return self.dict[shop_id]
    
def connect_service_buss():
    connstr = os.environ["SERVICEBUS_CONNECTION_STR"]

    client: ServiceBusClient = ServiceBusClient.from_connection_string(connstr)
        

def check_if_webhook(response:dict) -> dict[str, str] | None:
    if response["eventName"] == "TestMessage":
        return {"status":"200"}
    else:
        pass

