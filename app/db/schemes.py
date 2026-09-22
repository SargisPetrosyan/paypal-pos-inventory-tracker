import uuid
from dataclasses import dataclass
from typing import Sequence
import logging
from datetime import datetime

from sqlmodel.sql._expression_select_cls import SelectOfScalar
from sqlmodel import Session, select

from app.db.models import InventoryBalanceUpdateModel

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class InventoryBalanceUpdateRepository:
    session: Session

    def store_updated_inventory_data(
        self, inventory_update: list[InventoryBalanceUpdateModel]
    ) -> None:

        try:
            for i in inventory_update:
                self.session.add(instance=i)
            self.session.commit()
            for item in inventory_update:
                self.session.refresh(item)
            logger.info(
            "Stored %d records | timestamp: %i",
                len(inventory_update),
                inventory_update[0].timestamp,
                )
        except Exception as e:
            self.session.rollback()
            raise e

    def get_product_data(
        self,
        timestamp: datetime,
        organization_uuid: uuid.UUID,
        variant_uuid: uuid.UUID,
        product_uuid: uuid.UUID,
        before: int,
        after: int,
    ) -> Sequence[InventoryBalanceUpdateModel]:

        statement: SelectOfScalar[InventoryBalanceUpdateModel] = select(
            InventoryBalanceUpdateModel
        ).where(
            InventoryBalanceUpdateModel.timestamp == timestamp,
            InventoryBalanceUpdateModel.organization_uuid == organization_uuid,
            InventoryBalanceUpdateModel.variant_uuid == variant_uuid,
            InventoryBalanceUpdateModel.product_uuid == product_uuid,
            InventoryBalanceUpdateModel.before == before,
            InventoryBalanceUpdateModel.after == after,
        )

        results: Sequence[InventoryBalanceUpdateModel] = self.session.exec(
            statement=statement
        ).all()
        return results
