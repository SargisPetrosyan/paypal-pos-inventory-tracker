from typing import Any
from pydantic import BaseModel
import os

class Updates(BaseModel):
    updatedRange: str 

class RowEditResponse(BaseModel):
    spreadsheetId: str
    updates:Updates


class GoogleCredentials:
    def __init__(self) -> None:
        try:
            self.type:str = "service_account"
            self.project_id = "decent-carving-489308-g3"
            self.private_key_id: str = os.environ['GOOGLE_PRIVATE_KEY_ID']
            self.private_key: str = os.environ['GOOGLE_PRIVATE_KEY']
            self.client_email: str = os.environ['GOOGLE_CLIENT_EMAIL']
            self.client_id: str = os.environ['GOOGLE_CLIENT_ID']
            self.auth_uri="https://accounts.google.com/o/oauth2/auth"
            self.token_uri="https://oauth2.googleapis.com/token"
            self.auth_provider_x509_cert_url: str="https://www.googleapis.com/oauth2/v1/certs"
            self.client_x509_cert_url: str=os.environ['CLIENT_X509_CERT_URL']
            self.universe_domain:str = "googleapis.com"
        except KeyError:
            raise KeyError("Some of Google Credentials file info is not exist")
    
    def get_credentials(self)  -> dict[str, Any]:
        return self.__dict__