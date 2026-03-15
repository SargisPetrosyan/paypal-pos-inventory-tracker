from hmac import new
from typing import Any
from dotenv import load_dotenv
from abc import abstractmethod,ABC
import logging

import httpx
import rich

from app.constants import ART_AND_CRAFT_NAME, CAFE_NAME, DALA_SHOP_NAME, SHOPS
from app.models.webhook import WebhookCheck
from app.utils import CredentialContext, PaypalTokenData
load_dotenv()

logger: logging.Logger = logging.getLogger(name=__name__)

class WebhookManager(ABC):

    @abstractmethod
    def create_subscription(self)-> None:
        raise NotImplementedError
    
    @abstractmethod
    def check_subscription(self)-> None | WebhookCheck:
        raise NotImplementedError
    
    @abstractmethod
    def delete_subscription(self)-> None:
        raise NotImplementedError
    
    @abstractmethod
    def update_subscription(self,)-> None:
        raise NotImplementedError

class WebhookSubscriptionClient(WebhookManager):
    def __init__(self, shop_name:str) -> None:
        self.shop_name:str = shop_name
        self.creds_manager: PaypalTokenData = PaypalTokenData(shop_name=self.shop_name)
        self.credential_context = CredentialContext(shop_name=shop_name)

    def create_subscription(self) -> None:
        access_token: str = self.creds_manager._get_access_key()
        data: dict[str,Any] = {
        "uuid": self.credential_context.subscription_uuid,
        "transportName": "WEBHOOK",
        "eventNames": self.credential_context.events,
        "destination": self.credential_context.destination_url,
        "contactEmail": self.credential_context.mail,
        }
        logger.info(msg="creating subscription")
        response: httpx.Response = httpx.post(
            url='https://pusher.izettle.com/organizations/self/subscriptions',
            json=data,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=15)
        response.raise_for_status()
        logger.info(msg=f"created subscription for shop {self.shop_name} response : {response.json()}")

    def check_subscription(self) -> None | WebhookCheck:
        access_token: str = self.creds_manager._get_access_key()
        result: httpx.Response = httpx.get(
        url='https://pusher.izettle.com/organizations/self/subscriptions',
        
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
        result.raise_for_status()
        converted: list[dict[str,str]] | None = result.json()
        logger.info(msg=f"subscriptions for {self.shop_name} count:{len(result.json())} data: {result.json()}")
        if not converted:
            return None
        validated_model:WebhookCheck = WebhookCheck.model_validate(obj=converted[0])
        return validated_model
    
    def delete_subscription(self) -> None:
        access_token: str = self.creds_manager._get_access_key()
        logger.info(msg=f"deleting subscription")
        httpx.delete(
        url=f"https://pusher.izettle.com/organizations/self/subscriptions/{self.credential_context.subscription_uuid}",
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
        logger.info(f"deleted shop {self.shop_name} subscription ")


    def update_subscription(self ) -> None:
        access_token: str = self.creds_manager._get_access_key()
        data: dict[str,Any] = {
        "eventNames": self.credential_context.events,
        "destination": self.credential_context.destination_url,
        "contactEmail": self.credential_context.mail,
    }
        logger.info(msg=f"updating subscription")
        response: httpx.Response = httpx.put(
        url=f'https://pusher.izettle.com/organizations/self/subscriptions/{self.credential_context.subscription_uuid}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        },
        json=data)

        logger.info(msg=f"updated Dala shop subscription{response.json()}")

def delete_webhooks() -> None:
    for shop in SHOPS:
        shop_webhook_client = WebhookSubscriptionClient(shop_name=shop)
        subscription: None | WebhookCheck = shop_webhook_client.check_subscription()
        if not subscription or subscription.status is not 'ACTIVE':
            if not subscription:
                logger.info(msg=f"there is not any subscription for {shop}")
                continue
            else:
                shop_webhook_client.delete_subscription()