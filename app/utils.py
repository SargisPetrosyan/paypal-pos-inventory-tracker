from datetime import  datetime, timedelta
import json
import logging
from typing import Any
from fastapi import Request
from gspread.worksheet import JSONResponse
import pytz
from app.constants import (
    ART_CRAFT_FOLDER_ID,
    CAFFE_FOLDER_ID,
    DALASHOP_FOLDER_ID,
    MONTH_PRODUCT_STOCK_IN_NAME_COL_OFFSET,
    SHOP_SUBSCRIPTION_EVENTS,
    WEBHOOK_ENDPOINT_NAME)
from app.google_drive.client import GoogleDriveClient, SpreadSheetClient
from app.google_drive.drive_manager import GoogleDriveFileManager
from app.google_drive.sheet_manager import SpreadSheetFileManager
from datetime import datetime, timezone
import os
from app.constants import (
    DALA_SHOP_NAME,
    ART_AND_CRAFT_NAME,
    CAFE_NAME,
)
from app.models.google_drive import RowEditResponse

logger: logging.Logger = logging.getLogger(name=__name__)
import os
from dotenv import load_dotenv

load_dotenv()

logger: logging.Logger = logging.getLogger(name=__name__)

class EnvVariablesGetter:

    @staticmethod
    def get_env_variable(variable_name:str) -> str:
        variable: str | None = os.getenv(key=variable_name)

        if not variable:
            logger.critical(f"env variable by name '{variable_name}' cant be NONE ")
            raise TypeError(f"env variable by name '{variable_name}' cant be NONE ")
    
        return variable


class FileName:
    def __init__(self, date: datetime) -> None:
        logger.info(f"initializing file name")
        self.year: str = str(object=date.year)
        self.year_folder_name: str = str(object=date.year)
        self.month: str = str(object=date.month).zfill(2)
        self.day: str = str(object=date.day).zfill(2)
        self.day_worksheet_name: str = self.day
        self.month_file_name: str = str(object=date.strftime("%B"))
        self.day_file_name: str = f"{self.year}-{self.month}-{self.month_file_name}"
        self.month_worksheet_name: str = self.day_file_name
        self.monthly_report_file_name: str = f"{self.year}-monthly report"
        self.month_stock_in_and_out_col_index: int = int(self.day) + MONTH_PRODUCT_STOCK_IN_NAME_COL_OFFSET
        self.month_stock_out_row_index:int = int(self.day) + 1
        logger.info(f"file name was created 'file_name: {self.day_file_name}'")


def sheet_exist(items: dict[str, int], sheet_name: str) -> int | None:
    for sheet, index in items.items():
        if sheet == sheet_name:
            return index
    return None

def get_row_from_response(response: JSONResponse) -> int:
    product_update_data: str = response["updates"]["updatedRange"]
    product_row_position: str = product_update_data.split("!")[-1]
    if ":" in product_row_position:
        product_row_number: str = product_row_position.split(":")[0][1:]
        return int(product_row_number)
    else:
        product_row_number: str = product_row_position[0][1:]
        return int(product_row_number)


class ManagersCreator:
    def __init__(self) -> None:
        self._spreadsheet_client = SpreadSheetClient()
        self._google_drive_client = GoogleDriveClient()
        self._spreadsheet_manager = SpreadSheetFileManager(
            client=self._spreadsheet_client
        )
        self._google_drive_manager = GoogleDriveFileManager(
            client=self._google_drive_client
        )

    @property
    def google_drive_manager(self) -> GoogleDriveFileManager:
        return self._google_drive_manager

    @property
    def spreadsheet_manager(self) -> SpreadSheetFileManager:
        return self._spreadsheet_manager


class ZettleCredsPathManager:
    def __init__(self,shop_name:str) -> None:      
        BASE_DIR: str = os.path.dirname(p=os.path.abspath(path=__file__))
        self.token_path: str = os.path.abspath(
            path=os.path.join(BASE_DIR, f"creds/zettle/{shop_name}_access_token.json")
        )

        self.credentials_path: str = os.path.abspath(
            path=os.path.join(BASE_DIR, f"creds/zettle/{shop_name}_credentials.json")
        )

class CredentialContext():
    def __init__(self,shop_name:str) -> None:
        self.name: str = shop_name
        self._subscription_uuid: str | None = os.getenv(key=f"ZETTLE_{shop_name.upper()}_SUBSCRIPTION_UUID")
        self._destination_url: str | None = os.getenv(key="DESTINATION_URL")
        self._mail: str | None = os.getenv(key="MAIL")
        self.events: list[str] = SHOP_SUBSCRIPTION_EVENTS

    @property
    def subscription_uuid(self)-> str:
        if self._subscription_uuid is None:
            raise TypeError(f"{self.name} subscription_uuid cant be None")
        return self._subscription_uuid 
    
    @property
    def destination_url(self)-> str:
        if self._destination_url is None:
            raise TypeError(f"{self.name} destination_url cant be None")
        return self._destination_url + WEBHOOK_ENDPOINT_NAME
    
    @property
    def mail(self)-> str:
        if self._mail is None:
            raise TypeError(f"{self.name} mail cant be None")
        return self._mail 
    
class DateRangeBuilder:
    def __init__(self,end_date:datetime,interval_by_hours:int) -> None:
        start_date:datetime = end_date - timedelta(hours=interval_by_hours)
        self.start_date:str = start_date.isoformat()
        self.end_date:str = end_date.isoformat()


class OrganizationsNameMappedId:
    def __init__(self) -> None:
        self.organizations: dict[str | None, str] = {
            os.getenv("ZETTLE_ART_ORGANIZATION_UUID"):ART_AND_CRAFT_NAME,
            os.getenv("ZETTLE_DALA_ORGANIZATION_UUID"):DALA_SHOP_NAME,
            os.getenv("ZETTLE_CAFE_ORGANIZATION_UUID"):CAFE_NAME,
        } 

    def get_name_by_id(self,shop_id:str) -> str:
        organization_name: str | None = self.organizations.get(shop_id,None)
        if not organization_name:
            raise TypeError("organization uuid is missing")
        return organization_name

async def json_to_dict(request:Request)-> dict:
    body: bytes = await request.body()
    data = json.loads(body)
    data["payload"] = json.loads(data["payload"])
    return data

def utc_to_local(utc_dt:datetime) -> datetime:
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def get_folder_id_by_shop_id(shop_id:str):
    dala_shop_organization_id: str = EnvVariablesGetter.get_env_variable(variable_name='ZETTLE_DALA_ORGANIZATION_UUID')
    art_shop_organization_id: str = EnvVariablesGetter.get_env_variable(variable_name='ZETTLE_ART_ORGANIZATION_UUID')
    caffe_shop_organization_id = ''

    shop_ids: dict[str, str] = {
        dala_shop_organization_id:DALASHOP_FOLDER_ID,
        art_shop_organization_id:ART_CRAFT_FOLDER_ID,
        caffe_shop_organization_id:CAFFE_FOLDER_ID,
    }

    return shop_ids[shop_id]

def extract_row_from_notation(response:RowEditResponse) -> int:
    range: str = response.updates.updatedRange
    split: str = (range.split(":"))[1]
    row  = int(''.join(filter(lambda x: x.isdigit(), split)))
    return row


def time_offset() -> timedelta:
    stockholm_tz = pytz.timezone('Europe/Stockholm')
    return stockholm_tz.utcoffset(datetime.now())