import os
from typing import Any

class PaypalCredentials:
    def __init__(self,shop_name:str) -> None:
        self.client_id: str =os.environ[f"{shop_name.upper()}_CLIENT_ID"]
        self.key: str = os.environ[f"{shop_name.upper()}_KEY"]
        self.grant_type	 = "urn:ietf:params:oauth:grant-type:jwt-bearer"
        self.auth_url = "https://oauth.zettle.com/token"
        self.headers = "application/x-www-form-urlencoded"

    def get_credentials(self) -> dict[str, Any]:
        return self.__dict__
