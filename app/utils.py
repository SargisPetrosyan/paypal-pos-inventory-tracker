from datetime import datetime, timedelta
import os
import json      
import logging
import hmac
import hashlib
from uuid import UUID
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from typing import Sequence
from app.db.models import ZettleSigningKey


from fastapi import HTTPException, Request
import httpx
import pytz
import rich


from app.constants import (
    DALA_SHOP_NAME,
    PAYPAL_AUTH_URL,
    PAYPAL_GRANT_TYPE,
    PAYPAL_HEADERS,
    SHOP_SUBSCRIPTION_EVENTS,
    SHOPS,
    UTC_TIMEZONE_NAME,
    ACCESS_KEY_EXPIRES_DATE,
    WEBHOOK_NAME
)
from app.models.webhook import AccessToken

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class PaypalAccessTokenManager:
    shop_name: str
    _access_key: str | None = None
    _access_token_dict: dict[str, str] = field(default_factory=dict)

    @property
    def access_key(self) -> str:
        if not self._access_key:
            raise ValueError("access_key is empty")
        return self._access_key

    @access_key.setter
    def access_key(self, access_key:str):
        self._access_key = access_key

    def _expired_or_empty(self, current_date: datetime):
        expires_date: str | None = self._access_token_dict.get(ACCESS_KEY_EXPIRES_DATE)
        if not expires_date:
            return True
        date_object: datetime = datetime.strptime(expires_date, "%Y-%m-%d %H:%M:%S")
        return date_object <= current_date
    
    async def get_access_key(self) -> str:
        #change it to utc---------------------
        date: datetime = datetime.now()

        if self._expired_or_empty(current_date=date):
            headers: dict[str, str] = {"Content-Type": PAYPAL_HEADERS}
            url: str = PAYPAL_AUTH_URL

            data: dict[str, str] = {
                "grant_type": PAYPAL_GRANT_TYPE,
                "client_id": os.environ[f"{self.shop_name.upper()}_CLIENT_ID"],
                "assertion": os.environ[f"{self.shop_name.upper()}_KEY"],
            }

            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.post(
                    url=url,
                    data=data,
                    headers=headers,
                    timeout=15,
                )
            response.raise_for_status()

            formatted_data = response.json()

            validated_access_key: AccessToken = AccessToken.model_validate(formatted_data)
            rich.print(validated_access_key)
            #validate format data by pydantic

            self._access_token_dict[ACCESS_KEY_EXPIRES_DATE] = \
                str(datetime.now() + timedelta(seconds=validated_access_key.expires_in))
            
            self._access_token_dict["access_key"] = validated_access_key.access_token
            rich.print(self._access_token_dict)
        return self._access_token_dict["access_key"]


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
            os.environ["DESTINATION_URL"] + "/" + WEBHOOK_NAME
        )
        self.events = SHOP_SUBSCRIPTION_EVENTS


class ShopInfo:
    def __init__(self) -> None:
        self.dict = {
            UUID(os.environ["DALA_ORGANIZATION_UUID"]): "DALA_SHOP",
            UUID(os.environ["ART_ORGANIZATION_UUID"]): "ART_CRAFT",
            UUID(os.environ["CAFE_ORGANIZATION_UUID"]): "CAFE",
        }

    def get_shop_name_by_id(self, shop_id: UUID):
        return self.dict[shop_id]

def webhook_subscription(response: dict,) -> bool:
    if response.get("eventName") == "TestMessage":
        return True
    return False


async def webhook_validaton(request:Request, webhook_signing_keys:Sequence[str] | None) -> None:
    if not webhook_signing_keys:
        raise HTTPException(
            status_code=401,
            detail="No signing keys found for validation"
        )
    received_signature: str = request.headers.get("x-izettle-signature", "")
    raw_body: bytes = await request.body()
    validated:bool = False
    for Key_data in webhook_signing_keys:
        expected_signature: str = hmac.new(
            key=Key_data.encode(encoding="utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(expected_signature, received_signature):
            validated = True
            break
    if not validated:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )
async def load_webhook_signing_keys(session: AsyncSession) -> Sequence[str] | None:
    statement: SelectOfScalar = select(ZettleSigningKey.signing_key)
    results: Sequence[str] = (await session.execute(statement=statement)).scalars().all()
    return results

class SigningKeyEngine():
    def __init__(self)  -> None:
        self.engine: Engine = create_engine(os.environ["SIGNING_KEYS_DB_URL"])
        SQLModel.metadata.create_all(self.engine)