from datetime import date
from typing import Optional
from src.schemas.base import OrmModel

class SPartTypeInFailure(OrmModel):
    id: int
    name: str

class SDeviceInFailure(OrmModel):
    id: int
    serial_number: str

class SFailureRecordBase(OrmModel):
    device_id: int
    failure_date: date
    description: Optional[str] = None

class SFailureRecordCreate(OrmModel):
    """
    При создании указываем только device_id,
    дату отказа и описание.
    part_type_id подтянем из устройства.
    """
    device_id: int
    failure_date: date
    description: Optional[str] = None

class SFailureRecordUpdate(OrmModel):
    resolved_date: Optional[date] = None
    description: Optional[str]   = None

class SFailureRecordRead(SFailureRecordBase):
    id: int
    resolved_date: Optional[date]
    part_type: SPartTypeInFailure
    device: SDeviceInFailure
