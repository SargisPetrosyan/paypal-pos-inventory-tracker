from dotenv import load_dotenv

load_dotenv()

PAGE_SIZE_FOR_LIST_FILES: int = 100

#Shop names:
DALA_SHOP_NAME:str= "dala"
ART_AND_CRAFT_NAME:str = "art"
CAFE_NAME:str = "cafe"

SHOPS:tuple = (DALA_SHOP_NAME,ART_AND_CRAFT_NAME,CAFE_NAME)
TIME_INTERVAL_MINUTE:int = 30

SWEDEN_TIMEZONE_NAME ='Europe/Stockholm'

PAYPAL_GRANT_TYPE="urn:ietf:params:oauth:grant-type:jwt-bearer"
PAYPAL_AUTH_URL= "https://oauth.zettle.com/token"
PAYPAL_HEADERS= "application/x-www-form-urlencoded"

SHOPS:tuple = (DALA_SHOP_NAME,ART_AND_CRAFT_NAME,CAFE_NAME)

SHOP_SUBSCRIPTION_EVENTS:list[str] = ["InventoryBalanceChanged"]

