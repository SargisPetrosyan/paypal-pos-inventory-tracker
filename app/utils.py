from datetime import  datetime, timedelta
import json
import logging
from typing import Any
from fastapi import Request
from gspread.worksheet import JSONResponse
import httpx
import pytz
from app.constants import (
    ART_CRAFT_FOLDER_ID,
    CAFE_FOLDER_ID,
    DALASHOP_FOLDER_ID,
    MONTH_PRODUCT_STOCK_IN_NAME_COL_OFFSET,
    PAYPAL_AUTH_URL,
    PAYPAL_GRANT_TYPE,
    PAYPAL_HEADERS,
    SHOP_SUBSCRIPTION_EVENTS,
    SWEDEN_TIMEZONE_NAME,
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

    
class DateRangeBuilder:
    def __init__(self,end_date:datetime,interval_by_hours:int) -> None:
        start_date:datetime = end_date - timedelta(hours=interval_by_hours)
        self.start_date:str = start_date.isoformat()
        self.end_date:str = end_date.isoformat()


class OrganizationsNameMappedId:
    def __init__(self) -> None:
        self.organizations: dict[str | None, str] = {
            os.getenv("ART_ORGANIZATION_UUID"):ART_AND_CRAFT_NAME,
            os.getenv("DALA_ORGANIZATION_UUID"):DALA_SHOP_NAME,
            os.getenv("CAFE_ORGANIZATION_UUID"):CAFE_NAME,
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

def any_to_cet(date:datetime) -> datetime:
    SWEDEN_TIMEZONE: datetime = date.astimezone(pytz.timezone(SWEDEN_TIMEZONE_NAME))
    return SWEDEN_TIMEZONE

def get_folder_id_by_shop_id(shop_id:str):
    dala_shop_organization_id: str = os.environ['DALA_ORGANIZATION_UUID']
    art_shop_organization_id: str = os.environ['ART_ORGANIZATION_UUID']
    cafe_shop_organization_id = ''

    shop_ids: dict[str, str] = {
        dala_shop_organization_id:DALASHOP_FOLDER_ID,
        art_shop_organization_id:ART_CRAFT_FOLDER_ID,
        cafe_shop_organization_id:CAFE_FOLDER_ID,
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

def if_paypal_token_valid(expiration_date:datetime) -> bool:
    if datetime.now() > expiration_date:
        return False
    else:
        return True
    

class PaypalTokenData:
    def __init__(self, shop_name: str) :
        self.shop_name: str  = shop_name
        self.access_key: str = self._get_access_key()
    def _get_access_key(self)-> str:

        headers: dict[str, str] = {"Content-Type": PAYPAL_HEADERS}
        url: str = PAYPAL_AUTH_URL

        data: dict[str, str] = {
            "grant_type": PAYPAL_GRANT_TYPE,
            "client_id": os.environ[f"{ self.shop_name.upper()}_CLIENT_ID"],
            "assertion": os.environ[f"{ self.shop_name.upper()}_KEY"],
        }

        response = httpx.post(url=url, data=data, headers=headers)
        response.raise_for_status()

        formatted_data = response.json()

        self.expiration_date = os.environ[f"{ self.shop_name.upper()}_ACCESS_KEY_EXPIATION_DATE"] = str(datetime.now() + timedelta(
            seconds=formatted_data["expires_in"]
        ))

        return formatted_data['access_token']

class CredentialContext():
    def __init__(self,shop_name:str) -> None:
        self.name: str = shop_name
        self.subscription_uuid: str  = os.environ[f"{shop_name.upper()}_SUBSCRIPTION_UUID"]
        self.destination_url: str  = os.environ["DESTINATION_URL"] + "/inventory_tracker_webhook"
        self.mail: str = os.environ["MAIL"]
        self.events: list[str] = SHOP_SUBSCRIPTION_EVENTS
