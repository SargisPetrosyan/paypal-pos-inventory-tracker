from datetime import datetime
import os
from typing import Any
import httpx
from app.utils import PaypalTokenData
from dotenv import load_dotenv
import logging

load_dotenv()


logger: logging.Logger = logging.getLogger(name=__name__)

class PurchasesFetcher:
    def __init__(self,token_data:PaypalTokenData) -> None:
        self.toke_data: PaypalTokenData = token_data

    def get_purchases(self,start_date:datetime, end_date:datetime, descending: bool = False) -> dict[Any,Any]:
        logger.info(msg=f'get purchases by interval')

        response: httpx.Response = httpx.get(
            url='https://purchase.izettle.com/purchases/v2',
            params = {
                "startDate":start_date.isoformat(),
                "endDate":end_date.isoformat(),
                "descending":descending
            },
            headers={
                'Authorization': f'Bearer {self.toke_data.access_key}',
            },
        )
        response.raise_for_status()
        return response.json()
    
class ProductDataFetcher:
    def __init__(self,token_data:PaypalTokenData) -> None:
        self.token_data: PaypalTokenData = token_data
    def get_product_data(self,product_uuid:str, organization_id:str)  -> dict:
        response: httpx.Response = httpx.get(
        url=f'https://products.izettle.com/organizations/{organization_id}/products/{product_uuid}',
        headers={
            'Authorization': f'Bearer { self.token_data.access_key}',
        })
        response.raise_for_status()
        return response.json()



    