from datetime import date
from typing import Optional, List
from src.schemas.base import OrmModel
from src.device_types.schemas import (
    SDeviceTypeRead as DeviceTypeReadSchema,
    SPartTypeInDeviceType,
)
from src.locations.schemas import SLocationInDevice


class SDeviceBase(OrmModel):
    serial_number: str
    type_id: int
    purchase_date: Optional[date] = None
    warranty_end: Optional[date] = None
    current_location_id: Optional[int] = None
    status: str


class SDeviceCreate(SDeviceBase):
    pass


class SDeviceUpdate(OrmModel):
    serial_number: Optional[str] = None
    type_id: Optional[int] = None
    purchase_date: Optional[date] = None
    warranty_end: Optional[date] = None
    current_location_id: Optional[int] = None
    status: Optional[str] = None


# Define a simple schema for PartType used in Device - reusing existing schema
class SPartTypeSimple(SPartTypeInDeviceType):
    pass


# Определим вспомогательную схему для Device, которая не использует DeviceTypeReadSchema напрямую
class SSimpleDeviceTypeRead(OrmModel):
    id: int
    manufacturer: Optional[str]
    model: Optional[str]
    expected_lifetime_months: Optional[int]
    part_type_id: int
    # Change from dict to None, we'll use to_orm_model method instead
    part_types: Optional[SPartTypeSimple] = None
    created_by: int

    model_config = {"from_attributes": True}


class SDeviceRead(OrmModel):
    id: int
    serial_number: str
    purchase_date: Optional[date]
    warranty_end: Optional[date]
    status: str
    type: SSimpleDeviceTypeRead
    current_location: Optional[SLocationInDevice]
    created_by: int

    model_config = {"from_attributes": True}
