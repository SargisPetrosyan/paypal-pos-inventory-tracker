from uuid import UUID
from pydantic import BaseModel


class WebhookCheck(BaseModel):
    uuid: UUID
    status: str
