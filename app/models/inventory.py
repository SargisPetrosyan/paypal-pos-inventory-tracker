from pydantic import BaseModel
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID


class Updated(BaseModel):
    uuid: UUID
    timestamp: datetime
    userType: str
    clientUuid: UUID | None 

class BalanceBefore(BaseModel):
    organizationUuid: UUID
    locationUuid: UUID
    productUuid: UUID
    variantUuid: UUID
    balance: int

class BalanceAfter(BaseModel):
    organizationUuid: UUID
    locationUuid: UUID
    productUuid: UUID
    variantUuid: UUID
    balance: int

class Payload(BaseModel):
    organizationUuid: UUID
    updated: Updated
    balanceBefore: list[BalanceBefore]
    balanceAfter: list[BalanceAfter]
    externalUuid: None  | str

class InventoryBalanceUpdateValidation(BaseModel):
    organizationUuid: UUID
    messageUuid: UUID
    eventName: str
    messageId: UUID
    payload: Payload
    timestamp: datetime

@dataclass
class InventoryUpdateData():
    stock:int
    updated_value:int
    timestamp:datetime

class Test_request(BaseModel):
    text: str