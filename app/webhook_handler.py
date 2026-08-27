from httpx import request
from sqlmodel import Session
from app.db.schemes import InventoryBalanceUpdateRepository
from app.services import InventoryBalanceUpdater
from app.models.inventory import InventoryBalanceUpdateValidator
import logging
from sqlalchemy import Engine

logger: logging.Logger = logging.getLogger(name=__name__)

class SubscriptionHandler:
    def process_subscription(
            self,
            inventory_update:InventoryBalanceUpdateValidator,
            engine:Engine,
            session:Session) -> None:
        
        logger.info(f"""
            Balance data: before={len(inventory_update.payload.balanceBefore)} items,
            after={len(inventory_update.payload.balanceAfter)} items""")
        
        inventory_update_repository: InventoryBalanceUpdateRepository = InventoryBalanceUpdateRepository(engine=engine,session=session)

        inventory_balance_updater =  InventoryBalanceUpdater(
            inventory_balance_update=inventory_update, 
            inventory_update_repository=inventory_update_repository)
        
        inventory_balance_updater.store_inventory_update()


