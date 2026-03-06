from fastapi import FastAPI, Request
import logging

import uvicorn
from app.constants import TIME_INTERVAL_MINUTE
from app.google_drive.drive_sync_worker import HourlyWorkflowRunner
from app.utils import json_to_dict
from app.models.inventory import InventoryBalanceUpdateValidation
from contextlib import asynccontextmanager
from app.core.logging import setup_logger
from app.core.config import Database
from app.zettle.webhook_handler import SubscriptionHandler
from apscheduler.schedulers.background import BackgroundScheduler
from app.zettle.webhook_manager import delete_webhooks

setup_logger()
logger: logging.Logger = logging.getLogger(name=__name__)

database: Database = Database()
webhook_handler = SubscriptionHandler()
spreadsheet_updater = HourlyWorkflowRunner(database=database)

@asynccontextmanager
async def lifespan(app:FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=spreadsheet_updater.run,trigger="interval",minutes = TIME_INTERVAL_MINUTE)
    scheduler.start()
    yield
    delete_webhooks()
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post(path="/store_inventory_data_webhook")
async def store_inventory_data_webhook(request: Request) -> None | dict:
    data:dict = await request.json() 
    if data["eventName"] == "TestMessage": # need to change 
        logger.info("request for set subscription")
        return {"status":"200"}
    parsed_data:dict = await json_to_dict(request=request) # need to change 
    logger.info("request from webhook")
    validated_data: InventoryBalanceUpdateValidation = InventoryBalanceUpdateValidation.model_validate(obj=parsed_data)
    webhook_handler.process_subscription(inventory_update=validated_data, database=database)


 