from datetime import datetime
from typing import Sequence
from sqlalchemy import Engine
from sqlmodel import  Session,select
from app.db.models import InventoryBalanceUpdateModel
from sqlmodel.sql._expression_select_cls import SelectOfScalar
import uuid

import logging

logger: logging.Logger = logging.getLogger(name=__name__)

class  InventoryBalanceUpdateRepository():
    def __init__(self,engine:Engine, session:Session) -> None:
        self.engine: Engine  = engine
        self.session: Session = session
        
    def store_updated_inventory_data(self,inventory_update: list[InventoryBalanceUpdateModel]) -> None:
        for i in inventory_update:
            self.session.add(instance=i)
        self.session.commit()
        for item in inventory_update:
            self.session.refresh(item)
        logger.info(f"Stored {len(inventory_update)} records | timestamp: {inventory_update[0].timestamp}")
    
    def get_product_data(
            self,
            datetime: datetime, 
            organization_uuid:uuid.UUID,
            variant_id:uuid.UUID,
            product_id:uuid.UUID,
            before: int,
            after: int, ) -> Sequence[InventoryBalanceUpdateModel]:
        
        
        statement: SelectOfScalar[InventoryBalanceUpdateModel] = select(InventoryBalanceUpdateModel) \
            .where(
                InventoryBalanceUpdateModel.timestamp == datetime,
                InventoryBalanceUpdateModel.shop_id == organization_uuid,
                InventoryBalanceUpdateModel.variant_id == variant_id,
                InventoryBalanceUpdateModel.product_id == product_id,
                InventoryBalanceUpdateModel.before == before,
                InventoryBalanceUpdateModel.after == after,
                )
        
        results: Sequence[InventoryBalanceUpdateModel] = self.session.exec(statement=statement).all()
        return results
        
            