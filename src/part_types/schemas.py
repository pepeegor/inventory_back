from typing import List, Optional
from src.schemas.base import OrmModel

class SDeviceTypeInPartType(OrmModel):
    """
    Краткая схема для вложения в PartType:
    отображает id и основные поля DeviceType,
    без избыточных деталей.
    """
    id: int
    manufacturer: Optional[str]
    model: Optional[str]
    expected_lifetime_months: Optional[int]

class SPartTypeBase(OrmModel):
    """
    Базовые поля для создания и обновления PartType.
    """
    name: str
    description: Optional[str] = None
    expected_failure_interval_days: Optional[int] = None

class SPartTypeCreate(SPartTypeBase):
    """
    Схема для создания нового типа детали.
    Все поля из базовой.
    """
    pass

class SPartTypeUpdate(OrmModel):
    """
    Схема для частичного обновления:
    все поля опциональные.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    expected_failure_interval_days: Optional[int] = None

class SPartTypeRead(SPartTypeBase):
    """
    Схема для чтения PartType:
    включает id и вложенный список связанных DeviceType.
    """
    id: int
    device_types: List[SDeviceTypeInPartType]






