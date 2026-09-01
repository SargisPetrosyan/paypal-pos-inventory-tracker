import datetime
from sqlmodel import Field, SQLModel, DateTime
import uuid


class InventoryBalanceUpdateModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime.datetime = Field(default_factory=DateTime)
    organization_uuid: uuid.UUID = Field(default_factory=uuid.uuid4)
    product_uuid: uuid.UUID = Field(default_factory=uuid.uuid1)
    variant_uuid: uuid.UUID = Field(default_factory=uuid.uuid1)
    before: int
    after: int

    def __repr__(self) -> str:
        return f"""<InventoryBalanceUpdate(
        timestamp='{self.timestamp},
        before:{self.before},
        after:{self.after},
        change:{self.after}')>"""
    