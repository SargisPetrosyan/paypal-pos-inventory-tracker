from fastapi import FastAPI, Request, BackgroundTasks
import logging
from app.utils import  ShopInfo, json_to_dict
from app.models.inventory import InventoryBalanceUpdateValidation
from app.core.logging import setup_logger
from app.core.config import Database
from app.webhook_handler import SubscriptionHandler
import datetime
setup_logger()
shop_info = ShopInfo()
logger: logging.Logger = logging.getLogger(name=__name__)

webhook_handler = SubscriptionHandler()
app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(request: Request, backend_task: BackgroundTasks) -> None | dict:
    data:dict = await request.json()
    if data["eventName"] == "TestMessage":
        logger.debug("TestMessage subscription setup")
        return {"status":"200"}
    
    local_time: datetime.datetime = datetime.datetime.now()
    database: Database = Database(time=local_time)

    parsed_data:dict = await json_to_dict(request=request)
    
    # Validate payload format and content
    payload = parsed_data.get('payload', {})
    logger.info(f"Payload format: type={type(payload).__name__}, has_data={bool(payload)}")
    
    before_items = len(payload.get('balanceBefore', []))
    after_items = len(payload.get('balanceAfter', []))
    logger.info(f"Balance data: before={before_items} items, after={after_items} items")
    
    validated_data: InventoryBalanceUpdateValidation = InventoryBalanceUpdateValidation.model_validate(obj=parsed_data)
    logger.info(f"Webhook validated: {len(validated_data.payload.balanceBefore)} items")
    
    backend_task.add_task(
        func=webhook_handler.process_subscription,
        inventory_update=validated_data, 
        database=database)
    


    
    


 