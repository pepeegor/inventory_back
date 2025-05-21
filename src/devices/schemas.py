from datetime import date
from typing import Optional
from src.schemas.base import OrmModel
from src.device_types.schemas import SDeviceTypeRead
from src.locations.schemas import SLocationInDevice  # <-- изменено

class SDeviceBase(OrmModel):
    serial_number: str
    type_id: int
    purchase_date: Optional[date] = None
    warranty_end:  Optional[date] = None
    current_location_id: Optional[int] = None
    status: str

class SDeviceCreate(SDeviceBase):
    pass

class SDeviceUpdate(OrmModel):
    serial_number: Optional[str] = None
    type_id: Optional[int] = None
    purchase_date: Optional[date] = None
    warranty_end:  Optional[date] = None
    current_location_id: Optional[int] = None
    status: Optional[str] = None

class SDeviceRead(OrmModel):
    id: int
    serial_number: str
    purchase_date: Optional[date]
    warranty_end:  Optional[date]
    status: str
    type: SDeviceTypeRead
    current_location: Optional[SLocationInDevice]  
