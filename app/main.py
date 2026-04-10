from fastapi import FastAPI, Request, BackgroundTasks
import logging

from app.utils import  RequestIdempotency, ShopInfo, json_to_dict
from app.models.inventory import InventoryBalanceUpdateValidation, Test_request
from app.core.logging import setup_logger
from app.core.config import Database
from app.webhook_handler import SubscriptionHandler

setup_logger()
shop_info = ShopInfo()
logger: logging.Logger = logging.getLogger(name=__name__)

database: Database = Database()
webhook_handler = SubscriptionHandler()
request_idempotency = RequestIdempotency()

app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(request: Request, backend_task: BackgroundTasks) -> None | dict:
    data:dict = await request.json()
    if data["eventName"] == "TestMessage": # need to change 
        logger.info("request for set subscription")
        return {"status":"200"}
    parsed_data:dict = await json_to_dict(request=request) # need to change 
    validated_data: InventoryBalanceUpdateValidation = InventoryBalanceUpdateValidation.model_validate(obj=parsed_data)
    logger.info(f"request from {shop_info.get_shop_name_by_id(shop_id=validated_data.organizationUuid)} was validated successfully")
    backend_task.add_task(
        func=webhook_handler.process_subscription,
        inventory_update=validated_data, 
        database=database)
    


    
    


 