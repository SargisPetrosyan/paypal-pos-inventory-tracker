from datetime import datetime
from typing import Sequence
from sqlalchemy import Engine
from app.db.schemes import InventoryBalanceUpdateRepository
from app.models.inventory import InventoryBalanceUpdateValidator, Payload
from app.db.models import InventoryBalanceUpdateModel
from app.utils import any_to_cet
from dataclasses import dataclass

import logging

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class InventoryBalanceUpdater:
    inventory_balance_update: InventoryBalanceUpdateValidator
    inventory_update_repository: InventoryBalanceUpdateRepository

    def store_inventory_update(self) -> None:
        list_of_updates: list[InventoryBalanceUpdateModel] = []
        for i in range(len(self.inventory_balance_update.payload.balanceBefore)):
            payload: Payload = self.inventory_balance_update.payload
            local_timezone: datetime = any_to_cet(date=payload.updated.timestamp)
            product: Sequence[InventoryBalanceUpdateModel] = (
                self.inventory_update_repository.get_product_data(
                    datetime=local_timezone,
                    organization_uuid=payload.organizationUuid,
                    product_id=payload.balanceBefore[i].productUuid,
                    variant_id=payload.balanceBefore[i].variantUuid,
                    before=payload.balanceBefore[i].balance,
                    after=payload.balanceAfter[i].balance,
                )
            )

            if len(product) > 0:
                logger.debug(
                    f"Duplicate: product {payload.balanceBefore[i].productUuid}, variant {payload.balanceBefore[i].variantUuid}"
                )
                continue
            object = InventoryBalanceUpdateModel(
                timestamp=local_timezone,
                shop_id=payload.organizationUuid,
                product_id=payload.balanceBefore[i].productUuid,
                variant_id=payload.balanceBefore[i].variantUuid,
                before=payload.balanceBefore[i].balance,
                after=payload.balanceAfter[i].balance,
            )

            list_of_updates.append(object)
        self.inventory_update_repository.store_updated_inventory_data(
            inventory_update=list_of_updates
        )
