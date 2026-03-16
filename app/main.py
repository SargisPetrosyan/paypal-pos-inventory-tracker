from fastapi import FastAPI, Request
import logging

from app.utils import json_to_dict
from app.models.inventory import InventoryBalanceUpdateValidation
from app.core.logging import setup_logger
from app.core.config import Database
from app.webhook_handler import SubscriptionHandler

setup_logger()
logger: logging.Logger = logging.getLogger(name=__name__)

database: Database = Database()
webhook_handler = SubscriptionHandler()

app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(request: Request) -> None | dict:
    data:dict = await request.json() 
    if data["eventName"] == "TestMessage": # need to change 
        logger.info("request for set subscription")
        return {"status":"200"}
    parsed_data:dict = await json_to_dict(request=request) # need to change 
    logger.info("request from webhook")
    validated_data: InventoryBalanceUpdateValidation = InventoryBalanceUpdateValidation.model_validate(obj=parsed_data)
    webhook_handler.process_subscription(inventory_update=validated_data, database=database)


 