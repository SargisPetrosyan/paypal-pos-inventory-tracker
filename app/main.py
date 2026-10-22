import logging
from typing import Sequence

from sqlalchemy import Engine
from sqlmodel import Session
from fastapi import Depends, FastAPI, Request
from app.constants import WEBHOOK_SUCCEEDED_RETURN
from app.utils import create_signing_key_engine, load_webhook_signing_keys, webhook_validaton, webhook_subscription
from app.utils import (
    create_signing_key_engine,
    webhook_validaton,
    webhook_subscription,
)
from app.models.inventory import InventoryBalanceUpdateValidator
from app.core.logging import setup_logger
from app.core.config import get_session
from app.webhook_handler import SubscriptionHandler


setup_logger()

engine: Engine = create_signing_key_engine()
webhook_signing_keys: set[str] = load_webhook_signing_keys(engine)

logger: logging.Logger = logging.getLogger(name=__name__)

webhook_handler = SubscriptionHandler()
app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(
    request: Request,
    session: Session = Depends(dependency=get_session),
) :
    request_data: dict = await request.json()
    if webhook_subscription(response=request_data):
        return WEBHOOK_SUCCEEDED_RETURN
    await webhook_validaton(request=request,webhook_signing_keys=webhook_signing_keys)
    inventory_update: InventoryBalanceUpdateValidator = (
        InventoryBalanceUpdateValidator.model_validate(obj=request_data)
    )
    logger.info(
        "Webhook validated: %d items",len(inventory_update.payload.balance_before)
    )
    return await webhook_handler.process_subscription(inventory_update=inventory_update,session=session)
