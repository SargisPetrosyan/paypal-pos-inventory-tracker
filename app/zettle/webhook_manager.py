from typing import Any
from abc import abstractmethod, ABC

import logging
from dataclasses import dataclass, field
import httpx
from fastapi import Request

from app.constants import SHOPS
from app.models.webhook import WebhookCheck
from app.utils import CredentialContext, PaypalAccessTokenManager
import hashlib
import hmac

logger: logging.Logger = logging.getLogger(name=__name__)


class WebhookManager(ABC):
    @abstractmethod
    def create_subscription(self) -> None| dict:
        raise NotImplementedError

    @abstractmethod
    def check_subscription(self) -> None | WebhookCheck:
        raise NotImplementedError

    @abstractmethod
    def delete_subscription(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_subscription(
        self,
    ) -> None:
        raise NotImplementedError


@dataclass
class WebhookSubscriptionClient(WebhookManager):
    shop_name: str
    access_token_manager: PaypalAccessTokenManager
    subscription_config: CredentialContext

    def create_subscription(self) -> None | dict:
        access_token: str = self.access_token_manager.get_access_key()
        data: dict[str, Any] = {
            "uuid": self.subscription_config.subscription_uuid,
            "transportName": "WEBHOOK",
            "eventNames": self.subscription_config.events,
            "destination": self.subscription_config.destination_url,
            "contactEmail": self.subscription_config.mail,
        }
        logger.info(msg="creating subscription")
        response: httpx.Response = httpx.post(
            url="https://pusher.izettle.com/organizations/self/subscriptions",
            json=data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        response.raise_for_status()
        subscription: dict[str, Any] = response.json()
        logger.info("Created webhook subscription for shop %s", self.shop_name)
        return subscription

    def check_subscription(self) -> None | WebhookCheck:
        access_token: str = self.access_token_manager.get_access_key()
        result: httpx.Response = httpx.get(
            url="https://pusher.izettle.com/organizations/self/subscriptions",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        result.raise_for_status()
        converted: list[dict[str, str]] | None = result.json()
        logger.info(
            "Subscriptions for %s: %d", self.shop_name, len(converted or [])
        )
        if not converted:
            return None
        validated_model: WebhookCheck = WebhookCheck.model_validate(obj=converted[0])
        return validated_model

    def delete_subscription(self) -> None:
        access_token: str = self.access_token_manager.get_access_key()
        logger.info(msg="deleting subscription")
        httpx.delete(
            url=f"https://pusher.izettle.com/organizations/self/subscriptions/{self.subscription_config.subscription_uuid}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        logger.info("deleted shop  %a subscription",self.shop_name)

    def update_subscription(self) -> None:
        access_token: str = self.access_token_manager.get_access_key()
        data: dict[str, Any] = {
            "eventNames": self.subscription_config.events,
            "destination": self.subscription_config.destination_url,
            "contactEmail": self.subscription_config.mail,
        }
        logger.info(msg="updating subscription")
        response: httpx.Response = httpx.put(
            url=f"https://pusher.izettle.com/organizations/self/subscriptions/{self.subscription_config.subscription_uuid}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=data,
        )

        logger.info(msg=f"updated Dala shop subscription{response.json()}")


def delete_all_webhooks(subscription_client:WebhookSubscriptionClient) -> None:
    for shop in SHOPS:
        subscription: None | WebhookCheck = subscription_client.check_subscription()
        if not subscription or subscription.status is not "ACTIVE":
            if not subscription:
                logger.info(msg=f"there is not any subscription for {shop}")
                continue
            else:
                subscription_client.delete_subscription()


def ensure_subscriptions() -> None:
    for shop in SHOPS:
        subscription_config: CredentialContext = CredentialContext(shop_name=shop)
        access_token_manager: PaypalAccessTokenManager = PaypalAccessTokenManager(shop_name=shop)
        subscription_client: WebhookSubscriptionClient = WebhookSubscriptionClient(
            subscription_config=subscription_config, 
            access_token_manager=access_token_manager, 
            shop_name=shop)
        
        logger.info("ensure subscription for shop '%a'",shop)
        subscription: None | WebhookCheck = subscription_client.check_subscription()
        if not subscription or subscription.status != "ACTIVE":
            if not subscription:
                logger.info("subscription is '%a' for shop '%d'", subscription, shop)
                response = subscription_client.create_subscription()
            else:
                logger.info("subscription is '%a' for shop '%d'", subscription, shop)
                subscription_client.delete_subscription()
                subscription_client.create_subscription()

