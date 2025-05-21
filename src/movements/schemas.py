from datetime import datetime
from typing import Optional
from src.schemas.base import OrmModel

class SLocationMinimal(OrmModel):
    id: int
    name: str

class SUserMinimal(OrmModel):
    id: int
    full_name: str

class SMovementBase(OrmModel):
    from_location_id: Optional[int] = None
    to_location_id: int
    moved_at: datetime
    notes: Optional[str] = None

class SMovementCreate(SMovementBase):
    pass

class SMovementRead(OrmModel):
    id: int
    from_location: Optional[SLocationMinimal]
    to_location: SLocationMinimal
    moved_at: datetime
    performed_by_user: Optional[SUserMinimal]
    notes: Optional[str]