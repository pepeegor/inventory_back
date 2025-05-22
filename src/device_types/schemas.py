from typing import Optional
from src.schemas.base import OrmModel


class SPartTypeInDeviceType(OrmModel):
    id: int
    name: str


class SDeviceTypeBase(OrmModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    expected_lifetime_months: Optional[int] = None
    part_type_id: int


class SDeviceTypeCreate(SDeviceTypeBase):
    pass


class SDeviceTypeUpdate(OrmModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    expected_lifetime_months: Optional[int] = None
    part_type_id: Optional[int] = None


class SDeviceTypeRead(SDeviceTypeBase):
    id: int
    part_types: SPartTypeInDeviceType
    created_by: int

    model_config = {"from_attributes": True}
