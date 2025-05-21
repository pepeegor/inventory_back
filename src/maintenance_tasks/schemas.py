from datetime import date
from typing import Optional
from src.schemas.base import OrmModel

class SUserInTask(OrmModel):
    id: int
    full_name: str

class SDeviceInTask(OrmModel):
    id: int
    serial_number: str

class SMaintenanceTaskBase(OrmModel):
    device_id: int
    task_type: str
    scheduled_date: date
    completed_date: Optional[date]
    status: str
    assigned_to: Optional[int]
    notes: Optional[str]

class SMaintenanceTaskCreate(OrmModel):
    device_id: int
    task_type: str
    scheduled_date: date
    notes: Optional[str]
    status: str = "scheduled"

class SMaintenanceTaskUpdate(OrmModel):
    scheduled_date: Optional[date]
    completed_date: Optional[date]
    status: Optional[str]
    assigned_to: Optional[int]
    notes: Optional[str]

class SMaintenanceTaskRead(SMaintenanceTaskBase):
    id: int
    device: SDeviceInTask
    assigned_user: Optional[SUserInTask]
