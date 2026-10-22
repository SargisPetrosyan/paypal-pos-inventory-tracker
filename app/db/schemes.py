import uuid
from dataclasses import dataclass
from typing import Sequence
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from sqlmodel import select

from app.db.models import InventoryBalanceUpdateModel,ZettleSigningKey

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class InventoryBalanceUpdateRepository:
    session: AsyncSession

    async def store_updated_inventory_data(
        self, inventory_update: list[InventoryBalanceUpdateModel]
    ) -> dict:

        try:
            for i in inventory_update:
                self.session.add(instance=i)
            await self.session.commit()
            for item in inventory_update:
                await self.session.refresh(item)
            logger.info(
            "Stored %d records | timestamp: %s",
                len(inventory_update),
                str(inventory_update[0].timestamp),
                )
            return {"message": "Data registered in db"}
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_product_data(
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

        results= await self.session.execute(
            statement=statement
        ).scalars().all()
        return results


@dataclass
class SigningKeyRepository:
    session: AsyncSession
    
    async def get_signing_keys(self) -> Sequence[str]:
        statement: SelectOfScalar[str] = select(
            ZettleSigningKey.signing_key
        )
        results: Sequence[str] =await self.session.execute(statement=statement)
        
        items = results.scalars().all()