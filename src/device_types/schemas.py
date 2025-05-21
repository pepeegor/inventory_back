from typing import Optional
from src.schemas.base import OrmModel

class SPartTypeInDeviceType(OrmModel):
    """
    Минимальные данные о PartType для вложения в DeviceType.
    """
    id: int
    name: str

class SDeviceTypeBase(OrmModel):
    """
    Базовые поля для создания/обновления DeviceType.
    """
    manufacturer: Optional[str] = None
    model:        Optional[str] = None
    expected_lifetime_months: Optional[int] = None
    part_type_id: int

class SDeviceTypeCreate(SDeviceTypeBase):
    """
    Схема для POST /device-types.
    """
    pass

class SDeviceTypeUpdate(OrmModel):
    """
    Схема для PUT /device-types/{id}.
    """
    manufacturer: Optional[str] = None
    model:        Optional[str] = None
    expected_lifetime_months: Optional[int] = None
    part_type_id: Optional[int] = None

class SDeviceTypeRead(SDeviceTypeBase):
    """
    Схема для выдачи DeviceType:
    включает id и вложенный PartType.
    """
    id: int
    part_types: SPartTypeInDeviceType
