from typing import Any
from pydantic import BaseModel
import os

class Updates(BaseModel):
    updatedRange: str 

class RowEditResponse(BaseModel):
    spreadsheetId: str
    updates:Updates
