from dataclasses import dataclass
import logging
from datetime import datetime

from typing import Sequence
from app.db.schemes import InventoryBalanceUpdateRepository
from app.models.inventory import InventoryBalanceUpdateValidator, Payload
from app.db.models import InventoryBalanceUpdateModel
from app.utils import any_to_cet


logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class InventoryBalanceUpdater:
    inventory_balance_update: InventoryBalanceUpdateValidator
    inventory_update_repository: InventoryBalanceUpdateRepository

    def store_inventory_update(self) -> None:
        list_of_updates: list[InventoryBalanceUpdateModel] = []
        for id_, _ in enumerate(self.inventory_balance_update.payload.balance_before):
            payload: Payload = self.inventory_balance_update.payload
            local_timezone: datetime = any_to_cet(date=payload.updated.timestamp)
            product: Sequence[InventoryBalanceUpdateModel] = (
                self.inventory_update_repository.get_product_data(
                    timestamp=local_timezone,
                    organization_uuid=payload.organization_uuid,
                    product_uuid=payload.balance_before[id_].product_uuid,
                    variant_uuid=payload.balance_before[id_].variant_uuid,
                    before=payload.balance_before[id_].balance,
                    after=payload.balance_after[id_].balance,
                )
            )

            if len(product) > 0:
                logger.debug(
                    "Duplicate: product %d, variant %a",
                    payload.balance_before[id_].product_uuid, 
                    payload.balance_before[id_].variant_uuid,
                )
                continue
            inventory_balance:InventoryBalanceUpdateModel = InventoryBalanceUpdateModel(
                timestamp=local_timezone,
                organization_uuid=payload.organization_uuid,
                product_uuid=payload.balance_before[id_].product_uuid,
                variant_uuid=payload.balance_before[id_].variant_uuid,
                before=payload.balance_before[id_].balance,
                after=payload.balance_after[id_].balance,
            )

            list_of_updates.append(inventory_balance)
        self.inventory_update_repository.store_updated_inventory_data(
            inventory_update=list_of_updates
        )
