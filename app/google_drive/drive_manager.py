from app.google_drive.client import GoogleDriveClient
import os
import logging

logger: logging.Logger = logging.getLogger(name=__name__)

from typing import Any


ROOT_FOLDER: str | None = os.getenv(key="ROOT_FOLDER_ID")


class GoogleDriveFileManager:
    def __init__(self, client: GoogleDriveClient) -> None:
        self.client: GoogleDriveClient = client
        logger.info("'DriveFileManager' was created ")

    def create_year_folder(
        self,
        year: str,
        parent_folder_id: str,
    ) -> str:
        # create year folder
        year_folder: dict[Any, Any] = self.client.create_folder(
            folder_name=year, parent_folder_id=parent_folder_id
        )

        year_folder_id: str = year_folder["id"]
        # create nested month folder

        return year_folder_id

    def folder_exist_by_name(
        self, parent_folder_id: str, page_size: int, folder_name: str
    ) -> str | None:
        files_list: dict[str, Any] = self.client.list(
            q=f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed = false",
            fields="files(id, name)",
            page_size=page_size,
        )

        files: list[dict[str, str]] = files_list.get("files", [])

        if not files:
            return None

        # check if multiple files raise error
        if len(files) > 1:
            logger.warning(f"folder 'folder: {folder_name}' has duplicate")
            raise ValueError(f"{folder_name} has duplicate")
        return files[0]["id"]

    def get_spreadsheet_id_by_name(
        self, spreadsheet_name: str, parent_folder_id: str, page_size: int
    ) -> str | None:
        files_list: dict = self.client.list(
            q=f"name = '{spreadsheet_name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and '{parent_folder_id}' in parents and trashed = false",
            fields="files(id, name)",
            page_size=page_size,
        )

        files: list[dict[str, str]] = files_list.get("files", [])

        if not files:
            return None

        # check if multiple files raise error
        if len(files) > 1:
            raise ValueError(f"{spreadsheet_name} has duplicate")

        return files[0]["id"]

    def list_folder_files(self, folder_id: str) -> dict:
        return self.client.list(
            q=f"'{folder_id}' in parents and trashed=false",
            page_size=30,
            fields="files(id, name, mimeType)",
        )
