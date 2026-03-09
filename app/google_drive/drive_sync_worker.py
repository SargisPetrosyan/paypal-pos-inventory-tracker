from datetime import datetime, timedelta
import logging
import time

from sqlalchemy import Engine
from app.constants import  ART_AND_CRAFT_NAME, CAFE_NAME, DALA_SHOP_NAME, SHOPS, TIME_INTERVAL_MINUTE
from app.core.config import Database
from app.db.schemes import InventoryUpdateRepository
from app.google_drive.client import GoogleDriveClient, SpreadSheetClient
from app.google_drive.context import Context
from app.google_drive.drive_remote_updater import DriveSpreadsheetUpdater
from app.google_drive.drive_manager import GoogleDriveFileManager
from app.google_drive.services import DriveFileStructureEnsurer
from app.google_drive.sheet_manager import SpreadSheetFileManager
from app.models.product import PaypalProductData
from app.utils import PaypalTokenData
from app.zettle.services import InventoryManualDataCollector


logger: logging.Logger = logging.getLogger(name=__name__)

class HourlyWorkflowRunner:
    def __init__(self,database:Database) -> None:
        self.engine: Engine = database.engine
        self.shops: tuple[str, str, str]= SHOPS
        self.google_drive_client = GoogleDriveClient()
        self.spreadsheet_file_client = SpreadSheetClient()
        self.google_drive_file_manager = GoogleDriveFileManager(client=self.google_drive_client)
        self.spreadsheet_manager = SpreadSheetFileManager(client=self.spreadsheet_file_client)

    def run(self):
        
        start_date: datetime = datetime.now()
        end_date: datetime = start_date - timedelta(minutes=TIME_INTERVAL_MINUTE)
        # start_date: datetime = datetime.strptime("2026-01-13 12:36:22","%Y-%m-%d %H:%M:%S") #temporary
        # end_date: datetime = datetime.strptime("2026-01-13 16:00:00","%Y-%m-%d %H:%M:%S")
        logger.info(f"start checking manual changes start_date:{start_date}, end date 'end_date'")
        logger.info(msg=f"check manual changes for interval start:'{start_date}', end:'{end_date}'")

        repo_updater: InventoryUpdateRepository = InventoryUpdateRepository(engine=self.engine)
        
        for name in self.shops:
            logger.info(f"check manual changes for '{name}'")

            manual_collector = InventoryManualDataCollector(
                start_date= start_date, 
                end_date= end_date, 
                repo_updater=repo_updater,
                shop_name=name,
)

            # step 1 filter changed product data
            list_of_manual_products: list[PaypalProductData] | None = manual_collector.get_manual_changed_products()

            if not list_of_manual_products:
                logger.info(f"there is no manual changes for date interval start:{start_date}, end:{end_date}")
                continue

            for product in list_of_manual_products:
                time.sleep(8) #delay requests for google drive limitations
                context =Context(product=product)
                # step 2 check if google drive had proper file structure
                drive_file_ensurer = DriveFileStructureEnsurer(
                    google_drive_file_manager=self.google_drive_file_manager,
                    spreadsheet_file_manager=self.spreadsheet_manager)
                
                drive_file_ensurer.ensure_drive_file_structure(context=context)

                context.product = product
                # step 3 process manual changes to worksheet
                drive_file_updater = DriveSpreadsheetUpdater(context=context)
                drive_file_updater.process_data_to_worksheet()
                


        