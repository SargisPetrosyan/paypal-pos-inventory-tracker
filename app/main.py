import logging

from sqlmodel import Session
from fastapi import Depends, FastAPI, Request
from app.constants import WEBHOOK_SUCCEEDED_RETURN
from app.models.webhook import WebhookSubscription
from app.utils import ShopInfo, set_webhook_sign_key, webhook_validaton, webhook_subscription
from app.models.inventory import InventoryBalanceUpdateValidator
from app.core.logging import setup_logger
from app.core.config import get_session
from app.webhook_handler import SubscriptionHandler

webhook_signing_keys:set[str] = set()
setup_logger()
shop_info = ShopInfo()
logger: logging.Logger = logging.getLogger(name=__name__)

webhook_handler = SubscriptionHandler()
app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(
    request: Request,
    session: Session = Depends(dependency=get_session),
) :
    response: dict = await request.json()
    if webhook_subscription(response=response):
        validated_response: WebhookSubscription = WebhookSubscription.model_validate(response)
        set_webhook_sign_key(validated_response=validated_response,signing_key=webhook_signing_keys)
        return WEBHOOK_SUCCEEDED_RETURN
    await webhook_validaton(request=request,webhook_signing_keys=webhook_signing_keys)
    inventory_update: InventoryBalanceUpdateValidator = (
        InventoryBalanceUpdateValidator.model_validate(obj=response)
    )
    logger.info(
        "Webhook validated: %d items",len(inventory_update.payload.balance_before)
    )
    return await webhook_handler.process_subscription(inventory_update=inventory_update,session=session)
