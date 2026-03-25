from datetime import  datetime, timedelta
import json
import logging
from fastapi import Request
import httpx

import pytz
from datetime import datetime

from app.constants import PAYPAL_AUTH_URL, PAYPAL_GRANT_TYPE, PAYPAL_HEADERS, SHOP_SUBSCRIPTION_EVENTS, SWEDEN_TIMEZONE_NAME

logger: logging.Logger = logging.getLogger(name=__name__)
import os
from dotenv import load_dotenv

load_dotenv()

logger: logging.Logger = logging.getLogger(name=__name__)

class PaypalTokenData:
    def __init__(self, shop_name: str) :
        self.shop_name: str  = shop_name
        self.access_key: str = self._get_access_key()
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
    data["payload"] = json.loads(data["payload"])
    return data

def any_to_cet(date:datetime) -> datetime:
    SWEDEN_TIMEZONE: datetime = date.astimezone(pytz.timezone(SWEDEN_TIMEZONE_NAME))
    return SWEDEN_TIMEZONE


class CredentialContext():
    def __init__(self,shop_name:str) -> None:
        self.name: str = shop_name
        self.subscription_uuid: str  = os.environ[f"{shop_name.upper()}_SUBSCRIPTION_UUID"]
        self.destination_url: str  = os.environ["DESTINATION_URL"] + "/inventory_tracker_webhook"
        self.mail: str = os.environ["MAIL"]
        self.events: list[str] = SHOP_SUBSCRIPTION_EVENTS

class RequestIdempotency:
    def __init__(self) -> None:
        self.data:set = set()
    
    def if_idempotent(self,request:dict):
        logger.info("check request idempotency")
        message_uniqueid:str = request["messageUuid"]
        if message_uniqueid not in self.data:
            self.data.add(message_uniqueid)
            return False
        logger.warning("this request was not be processes because of idempotency")
        return True