from typing import Optional, List
from pydantic import ConfigDict
from src.schemas.base import OrmModel

class SLocationBase(OrmModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None

class SLocationCreate(SLocationBase):
    pass

class SLocationUpdate(OrmModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None

class SDeviceInLocation(OrmModel):
    id: int
    serial_number: str
    status: str

class SLocationRead(OrmModel):
    id: int
    name: str
    parent_id: Optional[int]
    description: Optional[str]
    created_by: int 
    children: List['SLocationRead'] = []
    devices: List[SDeviceInLocation] = []

    model_config = ConfigDict(from_attributes=True)
    
class SLocationInDevice(OrmModel):
    """
    Упрощённая схема локации для вложения в Device:
    только id и name.
    """
    id: int
    name: str

SLocationRead.model_rebuild()