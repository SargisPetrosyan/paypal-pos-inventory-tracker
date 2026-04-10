from sqlalchemy import Engine
from sqlmodel import  Session
from app.db.models import InventoryBalanceUpdateModel
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
    