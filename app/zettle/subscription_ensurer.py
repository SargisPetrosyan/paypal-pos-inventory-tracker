
from app.constants import ART_AND_CRAFT_NAME, DALA_SHOP_NAME, SHOPS
from app.models.webhook import WebhookCheck
from app.zettle.webhook_manager import WebhookSubscriptionClient
import logging
logger: logging.Logger = logging.getLogger(name=__name__)



for shop in SHOPS:
    logger.info(f"ensure subscription for shop '{shop}'")
    shop_webhook_client = WebhookSubscriptionClient(shop_name=shop)
    subscription: None | WebhookCheck = shop_webhook_client.check_subscription()
    if not subscription or subscription.status != 'ACTIVE':
        if not subscription:
            logger.info(f"subscription is '{subscription}' for shop '{shop}'")
            shop_webhook_client.create_subscription()
        else:
            logger.info(f"subscription is '{subscription} for shop '{shop}'")
            shop_webhook_client.delete_subscription()
            shop_webhook_client.create_subscription()