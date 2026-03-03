from typing import Any
import os
import httpx
from datetime import datetime,timedelta
import json
import logging
from app.utils import ZettleCredsPathManager
from datetime import datetime, timedelta
from app.models.zettle import (
    ZettleAccessToken, 
    ZettleCredentials, 
    ZettleNewAccessToken)
logger: logging.Logger = logging.getLogger(name=__name__)


client_id: str | None = os.getenv(key="ZETTLE_PRODUCT_READ_CLIENT_ID")
client_key: str | None= os.getenv(key="ZETTLE_PRODUCT_READ_KEY")


class ZettleTokenChecker:
    def __init__(self,path_manager:ZettleCredsPathManager) -> None:
        self._token_path:str = path_manager.token_path

    def is_valid(self) -> bool:
        logger.info("check if zettle access token is valid ")
        token_file: dict[str, Any] = self._get_token_file()
        self._zettle_token_info = ZettleAccessToken(**token_file)
        date_now: datetime = datetime.now()
        if  date_now > self._zettle_token_info.expiry:
            logger.info("zettle access token is not valid ")
            return False

        logger.info(msg="zettle access token is valid ")
        return True
    
    def token_file_exist(self) -> bool:
        return os.path.exists(path=self._token_path)
    
    def _get_token_file(self) -> dict[str,Any]:
        logger.info(msg="get access token file ")
        with open(file=self._token_path,mode='r',encoding='utf-8') as f:
            file:dict = json.load(fp=f)
        return file
    
    @property
    def access_token(self) -> str:
        return self._zettle_token_info.access_token

class ZettleCredentialsManager:
    def __init__(self, shop_name) -> None:
        self._path_manager: ZettleCredsPathManager = ZettleCredsPathManager(shop_name=shop_name)

    def _generate_expire_date(self)-> datetime:
        return datetime.now() + timedelta(seconds=7200)

    def _dump_access_token(self,access_token:ZettleNewAccessToken) -> None:
        logger.info(msg="dump new access token")
        expire_date:datetime = self._generate_expire_date()
        new_access_token_data: dict[str, str] = {
            "access_token": access_token.access_token,
            "expiry":str(object=expire_date)
        }

        with open(file=self._path_manager.token_path,mode="w") as file:
            json.dump(obj=new_access_token_data,fp=file)

    def _validate_access_token(self,access_token:dict) -> ZettleNewAccessToken:
        logger.info(msg="validate access token file")

        return ZettleNewAccessToken(**access_token)

    def _get_new_access_token(self)  -> str:
        logger.info("get new access token")
        with open( file=self._path_manager.credentials_path, mode='r') as f:
            file = json.load(fp=f)

        credentials = ZettleCredentials(**file)
        url: str = credentials.auth_url  # replace with real token URL

        headers: dict[str, str] = {"Content-Type": credentials.headers}

        data: dict[str, str] = {
            "grant_type": credentials.grant_type,
            "client_id": credentials.client_id,
            "assertion": credentials.key
        }

        response: httpx.Response = httpx.post(url=url, data=data, headers=headers)
        response.raise_for_status()

        access_token_info: ZettleNewAccessToken = self._validate_access_token(access_token=response.json())
        self._dump_access_token(access_token=access_token_info)
        return access_token_info.access_token

    
    def get_access_token(self) -> str:
        logger.info(msg="getting google drive credentials")
        creds_checker =ZettleTokenChecker(path_manager=self._path_manager)

        if creds_checker.token_file_exist() and creds_checker.is_valid():
            return creds_checker.access_token
        else:
            return self._get_new_access_token()