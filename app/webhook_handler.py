from httpx import request
from app.services import InventoryBalanceUpdater
from app.models.inventory import InventoryBalanceUpdateValidation
from app.core.config import Database
import logging

logger: logging.Logger = logging.getLogger(name=__name__)

class SubscriptionHandler:
    def process_subscription(self,inventory_update:InventoryBalanceUpdateValidation,database:Database,idempotent:bool) -> None:
        if idempotent:
            return
        inventory_balance_updater =  InventoryBalanceUpdater(inventory_balance_update=inventory_update, engine=database.engine)
        logger.info(msg="request was validated successfully!")
        inventory_balance_updater.store_inventory_update()


