import logging

from sqlmodel import Session
from app.db.schemes import InventoryBalanceUpdateRepository
from app.services import InventoryBalanceUpdater
from app.models.inventory import InventoryBalanceUpdateValidator

logger: logging.Logger = logging.getLogger(name=__name__)


class SubscriptionHandler:
    async def process_subscription(
        self,
        inventory_update: InventoryBalanceUpdateValidator,
        session: Session,
    ) :

        logger.info(
            "Balance data: before=%i items, after=%d items",
            len(inventory_update.payload.balance_before),
            len(inventory_update.payload.balance_after),
            )

        inventory_update_repository: InventoryBalanceUpdateRepository = (
            InventoryBalanceUpdateRepository(session=session)
        )

        inventory_balance_updater = InventoryBalanceUpdater(
            inventory_balance_update=inventory_update,
            inventory_update_repository=inventory_update_repository,
        )

        return inventory_balance_updater.store_inventory_update()