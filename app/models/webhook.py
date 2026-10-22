from uuid import UUID
from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Literal
from datetime import datetime

from app.models.inventory import BaseSchema

class WebhookCheck(BaseModel):
    uuid: UUID
    status: str

class AccessToken(BaseModel):
    access_token: str
    expires_in: int

class WebhookSubscription(BaseSchema):
    uuid: str
    transport_name: Literal['WEBHOOK']
    event_names: list[str]
    updated: datetime
    destination: HttpUrl
    contact_email: EmailStr
    status: str
    signing_key: str
    
