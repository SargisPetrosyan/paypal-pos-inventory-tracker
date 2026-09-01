from datetime import datetime
from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel,ConfigDict
from pydantic.alias_generators import to_camel

#caseName to camel_case
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

class Updated(BaseSchema):
    uuid: UUID
    timestamp: datetime
    user_type: str
    client_uuid: UUID | None


class BalanceBefore(BaseSchema):
    organization_uuid: UUID
    location_uuid: UUID
    product_uuid: UUID
    variant_uuid: UUID
    balance: int


class BalanceAfter(BaseSchema):
    organization_uuid: UUID
    location_uuid: UUID
    product_uuid: UUID
    variant_uuid: UUID
    balance: int


class Payload(BaseSchema):
    organization_uuid: UUID
    updated: Updated
    balance_before: list[BalanceBefore]
    balance_after: list[BalanceAfter]
    external_uuid: None | str


class InventoryBalanceUpdateValidator(BaseSchema):
    organization_uuid: UUID
    message_uuid: UUID
    event_name: str
    message_id: UUID
    payload: Payload
    timestamp: datetime


@dataclass
class InventoryUpdateData:
    stock: int
    updated_value: int
    timestamp: datetime


class TestRequest(BaseSchema):
    first_name: str
