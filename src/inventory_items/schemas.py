from typing import Optional
from pydantic import field_validator
from src.schemas.base import OrmModel
from datetime import date

class SInventoryItemBase(OrmModel):
    device_id: int
    found: bool
    condition: Optional[str]
    comments: Optional[str]

class SInventoryItemCreate(SInventoryItemBase):
    pass

class SInventoryItemUpdate(OrmModel):
    found: Optional[bool]
    condition: Optional[str]
    comments: Optional[str]

class SInventoryItemRead(SInventoryItemBase):
    id: int
    inventory_event_id: int
