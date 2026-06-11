from datetime import datetime
from typing import Sequence
from sqlalchemy import Engine
from sqlmodel import  Session,select
from app.db.models import InventoryBalanceUpdateModel
from sqlmodel.sql._expression_select_cls import SelectOfScalar
import uuid

import logging

logger: logging.Logger = logging.getLogger(name=__name__)

class  InventoryUpdateRepository():
    def __init__(self,engine) -> None:
        self.engine: Engine  = engine
        
    def store_updated_inventory_data(self,inventory_update: list[InventoryBalanceUpdateModel]) -> None:
        with Session(bind=self.engine) as session:
            for i in inventory_update:
                session.add(instance=i)
            session.commit()
            logger.info(f"products count: '{len(inventory_update)}' and timestamp:{inventory_update[0].timestamp} was stored in database")
    
    def get_product_data(
            self,
            datetime: datetime, 
            organization_uuid:uuid.UUID,
            variant_id:uuid.UUID,
            product_id:uuid.UUID,
            before: int,
            after: int, ) -> Sequence[InventoryBalanceUpdateModel]:
        with Session(bind=self.engine) as session:
            statement: SelectOfScalar[InventoryBalanceUpdateModel] = select(InventoryBalanceUpdateModel) \
                .where(
                    InventoryBalanceUpdateModel.timestamp == datetime,
                    InventoryBalanceUpdateModel.shop_id == organization_uuid,
                    InventoryBalanceUpdateModel.variant_id == variant_id,
                    InventoryBalanceUpdateModel.product_id == product_id,
                    InventoryBalanceUpdateModel.before == before,
                    InventoryBalanceUpdateModel.after == after,
                    )
            
            results: Sequence[InventoryBalanceUpdateModel] = session.exec(statement=statement).all()
            return results
        
            