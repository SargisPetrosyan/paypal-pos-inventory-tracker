import os
from dataclasses import dataclass, field

from app.constants import PAYPAL_AUTH_URL, PAYPAL_GRANT_TYPE, PAYPAL_HEADERS


@dataclass
class PaypalCredentials:
    shop_name: str
    key: str
    grant_type: str = PAYPAL_GRANT_TYPE
    auth_url: str = PAYPAL_AUTH_URL
    headers: str = PAYPAL_HEADERS
    client_id: str = field(init=False)

    def __post_init__(self):
        self.client_id: str = os.environ[f"{self.shop_name.upper()}_CLIENT_ID"]
