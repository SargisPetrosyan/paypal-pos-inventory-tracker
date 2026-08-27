from fastapi import FastAPI, Request, BackgroundTasks
import logging
from app.utils import  ShopInfo, check_if_webhook, json_to_dict
from app.models.inventory import InventoryBalanceUpdateValidation
from app.core.logging import setup_logger
from app.core.config import Database
from app.webhook_handler import SubscriptionHandler
import datetime

# service buss
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential

setup_logger()
shop_info = ShopInfo()
logger: logging.Logger = logging.getLogger(name=__name__)

webhook_handler = SubscriptionHandler()
app = FastAPI()

@app.post(path="/inventory_tracker_webhook")
async def store_inventory_data_webhook(request: Request, backend_task: BackgroundTasks) -> None | dict:
    response:dict = await request.json()
    check_if_webhook(response=response)
    
    local_time: datetime.datetime = datetime.datetime.now()
    database: Database = Database(time=local_time)

    inventory_update: InventoryBalanceUpdateValidation = InventoryBalanceUpdateValidation.model_validate(obj=response)
    logger.info(f"Webhook validated: {len(inventory_update.payload.balanceBefore)} items")
    
    backend_task.add_task(
        func=webhook_handler.process_subscription,
        inventory_update=inventory_update, 
        database=database)
    


    
    


 