from dotenv import load_dotenv
from typing import Literal
load_dotenv()

PAGE_SIZE_FOR_LIST_FILES: int = 100

# Shop names:
DALA_SHOP_NAME: Literal["dala"] = "dala"
ART_AND_CRAFT_NAME: Literal["art"] = "art"
CAFE_NAME: Literal["cafe"] = "cafe"

SHOPS: tuple = (DALA_SHOP_NAME, ART_AND_CRAFT_NAME, CAFE_NAME)
TIME_INTERVAL_MINUTE: int = 30

SWEDEN_TIMEZONE_NAME = "Europe/Stockholm"
UTC_TIMEZONE_NAME = "UTC"

PAYPAL_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"
PAYPAL_AUTH_URL = "https://oauth.zettle.com/token"
PAYPAL_HEADERS = "application/x-www-form-urlencoded"


SHOP_SUBSCRIPTION_EVENTS: list[str] = ["InventoryBalanceChanged"]

WEBHOOK_SUCCEEDED_RETURN:dict[str, str|dict] = {
    "status": "200",
    "response": {
        "message": "Webhook Succeeded",
    }
}

ACCESS_KEY_EXPIRES_DATE: str = "access_key_expiration_date"
WEBHOOK_NAME:str = "inventory_tracker_webhook"
