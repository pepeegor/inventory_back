from datetime import date
from typing import Optional
from src.schemas.base import OrmModel

class SDeviceInReport(OrmModel):
    id: int
    serial_number: str

class SUserInReport(OrmModel):
    id: int
    username: str
    full_name: str

class SWriteOffReportBase(OrmModel):
    device_id: int
    report_date: date
    reason: str
    disposed_by: Optional[int] = None
    approved_by: Optional[int] = None

class SWriteOffReportCreate(SWriteOffReportBase):
    pass

class SWriteOffReportUpdate(OrmModel):
    reason: Optional[str] = None
    disposed_by: Optional[int] = None
    approved_by: Optional[int] = None

class SWriteOffReportRead(SWriteOffReportBase):
    id: int
    device: SDeviceInReport
    disposed_by_user: Optional[SUserInReport]
    approved_by_user: Optional[SUserInReport]
