from app.google_drive.auth import get_drive_credentials
from typing import Any, Optional
import gspread
import os
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError #type:ignore
from googleapiclient.discovery import build #type:ignore
from gspread.spreadsheet import Spreadsheet


logger: logging.Logger = logging.getLogger(name=__name__)


root: str | None = os.getenv(key="ROOT_FOLDER_ID")


class GoogleDriveClient:
    def __init__(self) -> None:
        creds: Credentials = get_drive_credentials()
        try:
            logger.info("creating google drive client")
            self._client: Any = build(
                serviceName="drive", version="v3", credentials=creds
            )
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
        credentials: Credentials = get_drive_credentials()
        try:
            logger.info("SpreadSheetClient creation")
            self._client: gspread.Client = gspread.authorize(credentials=credentials)
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
