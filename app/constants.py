from typing import Literal
from xxlimited import Str
from dotenv import load_dotenv

load_dotenv()

PAGE_SIZE_FOR_LIST_FILES: int = 100

# names
WORKSHEET_SAMPLE_COPY_NAME: str = "Copy of WORKSHEET_SAMPLE"
WORKSHEET_SAMPLE_NAME: str = "WORKSHEET_SAMPLE"
DALAHOP_FOLDER_NAME: str = "DALASHOP"
ARTANDCRAFT_FOLDER_NAME: str = "ART_CRAFT"
CAFE_FOLDER_NAME: str = "DALA_CAFE"
WEBHOOK_ENDPOINT_NAME: str = "/store_inventory_data_webhook"
EMPTY_FIELD_NAME: str = "None"

# ids
DAY_TEMPLATE_ID = "1Xh5ZAwsr_SaF2GHQHmJZwhdZnQM-adSFiMrAAB7yc3s"
MONTHLY_TEMPLATE_ID: str = "1UvJ9bcsn6U2n9joXC55nEwPb0ifpRu1gUwAPe2og77g"
NESTED_FILE_ID: str = "1j6xLhBBkicEneFIlXWLhB56V0DMJiIxRA4vDDDhAeHI"
NESTED_FOLDER_ID: str = "1PNDivjpslR_dA2a5yZlE5l9lbfr7XWa4"
ROOT_FOLDER_ID: str = "1HlMXMD94ok0mFEP8k7QoGY3JZX8YjAQS"
DALASHOP_FOLDER_ID: str = "1kjWENsaqJWC7PeSXVD7IP5yVe4GZp1VP"
ART_CRAFT_FOLDER_ID: str = "1KtFC0c9PKaaX5r65ZKOihWigFwc2gYny"
CAFE_FOLDER_ID: str = "1VpgSGa9LzMKPFjLCOBs6vQazdawqOzHw"

# shop id's
ID_DALA_SHOP: str = "DALA_ID"
ID_ART_CRAFT: str = "ART_ID"
ID_DALA_CAFE: str = "CAFE_ID"

# day worksheet columns index
DAY_PRODUCT_NAME_COL: int = 1
DAY_PRODUCT_CATEGORY_COL: int = 2
DAY_PRODUCT_VARIANT: int = 3
DAY_PRODUCT_COST_PRICE_COL: int = 4
DAY_PRODUCT_SELLING_PRICE_COL: int = 5
DAY_PRODUCT_AND_VARIANT_ID_COL: int = 6
DAY_PRODUCT_STOCK_IN_COL: int = 7
DAY_PRODUCT_STOCK_OUT_COL: int = 8

# month worksheet columns index
MONTH_PRODUCT_NAME_COL: int = 1
MONTH_PRODUCT_CATEGORY_COL: int = 2
MONTH_PRODUCT_VARIANT_COL: int = 3
MONTH_PRODUCT_COST_PRICE_COL: int = 4
MONTH_PRODUCT_SELLING_PRICE_COL: int = 5
MONTH_PRODUCT_AND_VARIANT_ID_COL: int = 6
MONTH_PRODUCT_STOCK_IN_NAME_COL_OFFSET: int = 7
MONTH_PRODUCT_STOCK_OUT_NAME_ROW_OFFSET: int = 1

# month worksheet
MONTH_WORKSHEET_FIRST_CELL: str = "A2:A3"  # merged cells
MONTH_PRODUCT_DATA_CELL_RANGE: str = "A2:D2"

# webhook constants
SHOP_SUBSCRIPTION_EVENTS:list[str] = ["InventoryBalanceChanged"]

#Shop names:
DALA_SHOP_NAME:str= "dala"
ART_AND_CRAFT_NAME:str = "art"
CAFE_NAME:str = "cafe"

SHOPS:tuple = (DALA_SHOP_NAME,ART_AND_CRAFT_NAME,CAFE_NAME)
TIME_INTERVAL_MINUTE:int = 30

DRIVE_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# file and folder names 
GOOGLE_CREDENTIALS_FILE_NAME:str = 'google_credentials.json'
GOOGLE_TOKEN_FILE_NAME:str = 'google_token.json'

SWEDEN_TIMEZONE_NAME ='Europe/Stockholm'


PAYPAL_GRANT_TYPE="urn:ietf:params:oauth:grant-type:jwt-bearer"
PAYPAL_AUTH_URL= "https://oauth.zettle.com/token"
PAYPAL_HEADERS= "application/x-www-form-urlencoded"


