import logging

from sqlmodel import Session
from fastapi import Depends, FastAPI, Request, BackgroundTasks
from app.constants import WEBHOOK_SUCCEEDED_RETURN
from app.utils import ShopInfo, webhook_request
from app.models.inventory import InventoryBalanceUpdateValidator
from app.core.logging import setup_logger
from app.core.config import get_session
from app.webhook_handler import SubscriptionHandler

setup_logger()
shop_info = ShopInfo()
logger: logging.Logger = logging.getLogger(name=__name__)

webhook_handler = SubscriptionHandler()
app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(
    request: Request,
    backend_task: BackgroundTasks,
    session: Session = Depends(get_session),
) :

    response: dict = await request.json()
    if webhook_request(response=response):
        return WEBHOOK_SUCCEEDED_RETURN
    inventory_update: InventoryBalanceUpdateValidator = (
        InventoryBalanceUpdateValidator.model_validate(obj=response)
    )
    logger.info(
        "Webhook validated: %d items",len(inventory_update.payload.balance_before)
    )
    backend_task.add_task(
        func=webhook_handler.process_subscription,
        inventory_update=inventory_update,
        session=session,
    )
