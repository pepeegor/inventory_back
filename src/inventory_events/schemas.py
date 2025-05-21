from datetime import date
from typing import Optional, List
from src.schemas.base import OrmModel

class SInventoryEventBase(OrmModel):
    event_date: date
    location_id: int
    notes: Optional[str] = None

class SInventoryEventCreate(SInventoryEventBase):
    pass

class SInventoryEventUpdate(OrmModel):
    event_date: Optional[date] = None
    location_id: Optional[int] = None
    notes: Optional[str] = None

class SInventoryItemMinimal(OrmModel):
    id: int
    device_id: int
    found: bool
    condition: Optional[str]
    comments: Optional[str]

class SUserMinimal(OrmModel):
    id: int
    full_name: str

class SLocationMinimal(OrmModel):
    id: int
    name: str

class SInventoryEventRead(OrmModel):
    id: int
    event_date: date
    location: SLocationMinimal
    performed_by_user: Optional[SUserMinimal]
    notes: Optional[str]
    items: List[SInventoryItemMinimal] = []