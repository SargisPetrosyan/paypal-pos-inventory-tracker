import logging

from sqlalchemy import Engine
from fastapi import Depends, FastAPI, Request
from app.constants import WEBHOOK_SUCCEEDED_RETURN
from app.utils import (
    load_webhook_signing_keys,
    webhook_validaton,
    webhook_subscription)
from app.models.inventory import InventoryBalanceUpdateValidator
from app.core.logging import setup_logger
from app.core.config import get_inventory_db_session,get_signing_key_db_session
from app.webhook_handler import SubscriptionHandler
from sqlalchemy.ext.asyncio import AsyncSession


setup_logger()
logger: logging.Logger = logging.getLogger(name=__name__)

webhook_handler = SubscriptionHandler()
app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(
    request: Request,
    inventory_session: AsyncSession = Depends(dependency=get_inventory_db_session),
    signing_key_engine: AsyncSession = Depends(dependency=get_signing_key_db_session)

) :
    request_data: dict = await request.json()
    if webhook_subscription(response=request_data):
        return WEBHOOK_SUCCEEDED_RETURN
    webhook_signing_keys: set[str] | None = await load_webhook_signing_keys(engine=signing_key_engine)
    await webhook_validaton(request=request, webhook_signing_keys=webhook_signing_keys)
    inventory_update: InventoryBalanceUpdateValidator = (
        InventoryBalanceUpdateValidator.model_validate(obj=request_data)
    )
    logger.info(
        "Webhook validated: %d items",len(inventory_update.payload.balance_before)
    )
    return await webhook_handler.process_subscription(inventory_update=inventory_update,session=inventory_session)
