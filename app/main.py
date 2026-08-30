from fastapi import Depends, FastAPI, Request, BackgroundTasks
import logging

from sqlmodel import Session

from app.utils import ShopInfo, check_if_webhook, json_to_dict
from app.models.inventory import InventoryBalanceUpdateValidator
from app.core.logging import setup_logger
from app.core.config import DatabaseConnection, DatabaseConnection, get_session
from app.webhook_handler import SubscriptionHandler

setup_logger()
shop_info = ShopInfo()
logger: logging.Logger = logging.getLogger(name=__name__)

webhook_handler = SubscriptionHandler()
app = FastAPI()

database: DatabaseConnection = DatabaseConnection()


@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(
    request: Request,
    backend_task: BackgroundTasks,
    session: Session = Depends(get_session),
) -> None | dict:

    response: dict = await request.json()
    check_if_webhook(response=response)
    inventory_update: InventoryBalanceUpdateValidator = (
        InventoryBalanceUpdateValidator.model_validate(obj=response)
    )
    logger.info(
        f"Webhook validated: {len(inventory_update.payload.balanceBefore)} items"
    )
    backend_task.add_task(
        func=webhook_handler.process_subscription,
        inventory_update=inventory_update,
        engine=database.engine,
        session=session,
    )
