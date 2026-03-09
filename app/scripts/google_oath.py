import os.path
from app.constants import DRIVE_SCOPES
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import (
    Credentials as ExternalAccountAuthorized,
)
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
import logging


logger: logging.Logger = logging.getLogger(name=__name__)


def get_drive_credentials() -> Credentials:
    logger.info("getting google drive credentials")
    BASE_DIR: str = os.path.dirname(os.path.abspath(path=__file__))
    CREDENTIALS_PATH: str = os.path.abspath(
        path=os.path.join(BASE_DIR, "../../app/creds/google/credentials.json")
    )
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
            with open("token.pkl", mode="wb") as token_file:
                pickle.dump(obj=creds, file=token_file)

        else:
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=CREDENTIALS_PATH, scopes=DRIVE_SCOPES
            )
            creds = flow.run_local_server(port=0)
            assert credits is not None
            # Save the credentials for the next run
            logger.info("set up new token.json file")
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())  # type: ignore
    return creds  # type: ignore
