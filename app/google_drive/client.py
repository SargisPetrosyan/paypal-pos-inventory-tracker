from typing import Any, Mapping, Optional
import gspread
import os
import logging
from dotenv import load_dotenv
from gspread.spreadsheet import Spreadsheet
from googleapiclient.errors import HttpError #type:ignore
from googleapiclient.discovery import build #type:ignore
from google.oauth2 import service_account


class GoogleCredentials:
    def __init__(self) -> None:
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
    
    def get_credentials(self)  -> dict[str, Any]:
        return self.__dict__

logger: logging.Logger = logging.getLogger(name=__name__)

load_dotenv()

root: str | None = os.getenv(key="ROOT_FOLDER_ID")

class GoogleDriveClient:
    def __init__(self) -> None:
        google_creds = GoogleCredentials()
        creds_info:Mapping[str,str] = google_creds.get_credentials()

        SCOPES = ["https://www.googleapis.com/auth/drive"]

        try:
            creds: service_account.Credentials = service_account.Credentials.from_service_account_info(info=creds_info, scopes=SCOPES)
            logger.info("creating google drive client")
            self._client = build(serviceName="drive", version="v3", credentials=creds)
            logger.info("google drive client was created")
        except HttpError as error:
            logger.critical(f"Failed to build drive _client: {error}")
            raise RuntimeError(f"Failed to build drive _client: {error}")

    def list(self, page_size: int, q: str, fields: str) -> dict[str, str]:
        """List files matching a query."""
        results: Any = (
            self._client.files().list(q=q, pageSize=page_size, fields=fields).execute()
        )

        return results

    def copy(
        self,
        file_id: Optional[str],
        file_name: str | None,
        parent_folder_id: str,
    ) -> dict:
        """Duplicate a file and return metadata for the new copy."""
        return (
            self._client.files()
            .copy(
                fileId=file_id, body={"name": file_name, "parents": [parent_folder_id]}
            )
            .execute()
        )

    def delete(self, file_id: str) -> dict:
        """Delete drive file by id"""
        return self._client.files().delete(fileId=file_id).execute()

    def get(self, file_id: str) -> dict:
        return (
            self._client.files()
            .get(
                fileId=file_id,
            )
            .execute()
        )

    def create_folder(self, folder_name: str, parent_folder_id: str) -> dict:
        folder_metadata: dict[str, str | list] = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],  # parent folder ID
        }

        return self._client.files().create(body=folder_metadata, fields="id").execute()


class SpreadSheetClient:
    def __init__(self) -> None:
        google_creds = GoogleCredentials()
        creds: dict[str, Any] = google_creds.get_credentials()
        try:
            logger.info("SpreadSheetClient creation")
            self._client: gspread.Client = gspread.service_account_from_dict(info=creds)
            logger.info("SpreadSheetClient was create successfully")
        except HttpError as error:
            logger.critical("an occur error during creation 'SpreadSheetClient'")
            raise RuntimeError(f"Failed to build sheet client: {error}")

    def copy(self, field_id: str, title: str, folder_id: str) -> Spreadsheet:
        return self._client.copy(file_id=field_id, title=title, folder_id=folder_id)

    def open_by_key(
        self,
        spreadsheet_id: str,
    ) -> Spreadsheet:
        return self._client.open_by_key(key=spreadsheet_id)

    def get_worksheet(
        self,
        spreadsheet_id: str,
        worksheet_title: str,
    ) -> gspread.Worksheet:
        return self.open_by_key(spreadsheet_id=spreadsheet_id).worksheet(
            title=worksheet_title
        )

    def spreadsheets_sheets_copy_to(
        self, id: str, sheet_id: int, destination_spreadsheet_id: str
    ) -> None:
        self._client.http_client.spreadsheets_sheets_copy_to(
            id=id,
            sheet_id=sheet_id,
            destination_spreadsheet_id=destination_spreadsheet_id,
        )
