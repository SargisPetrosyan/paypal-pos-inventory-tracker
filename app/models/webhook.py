from uuid import UUID
from pydantic import BaseModel


class WebhookCheck(BaseModel):
    uuid: UUID
    status: str

class AccessToken(BaseModel):
    access_token: str
    expires_in: int