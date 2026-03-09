import os.path
from app.constants import DRIVE_SCOPES
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import (
    Credentials as ExternalAccountAuthorized,
)
import logging


logger: logging.Logger = logging.getLogger(name=__name__)


def get_drive_credentials() -> Credentials:
    logger.info("getting google drive credentials")
    BASE_DIR: str = os.path.dirname(os.path.abspath(path=__file__))
    TOKEN_PATH: str = os.path.abspath(
        path=os.path.join(BASE_DIR, "../../app/creds/google/token.json")
    )
    creds: Credentials | ExternalAccountAuthorized | None = None

    if os.path.exists(path=TOKEN_PATH):
        logger.warning("token file exist found start authentication")
        creds = Credentials.from_authorized_user_file(
            filename=TOKEN_PATH, scopes=DRIVE_SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.warning("creds was expired getting new token")
            creds.refresh(request=Request())
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())  # type: ignore
        else:
            raise ValueError("google Token is not valid")
    return creds  # type: ignore
