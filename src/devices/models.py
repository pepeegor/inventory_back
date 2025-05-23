from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.device_types.models import DeviceType
    from src.locations.models import Location
    from src.movements.models import Movement
    from src.inventory_items.models import InventoryItem
    from src.maintenance_tasks.models import MaintenanceTask
    from src.write_off_reports.models import WriteOffReport
    from src.failure_records.models import FailureRecord
    from src.users.models import User


class Device(Base):
    __tablename__ = "devices"

    id = Column(BigInteger, primary_key=True)
    serial_number = Column(String(100), unique=True, nullable=False)
    type_id = Column(BigInteger, ForeignKey("device_types.id"), nullable=False)
    purchase_date = Column(Date)
    warranty_end = Column(Date)
    current_location_id = Column(BigInteger, ForeignKey("locations.id"))
    status = Column(String(20), nullable=False)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    type = relationship("DeviceType", back_populates="devices")
    current_location = relationship("Location", back_populates="devices")
    movements = relationship("Movement", back_populates="device")
    inventory_items = relationship("InventoryItem", back_populates="device")
    maintenance_tasks = relationship("MaintenanceTask", back_populates="device")
    write_off_reports = relationship("WriteOffReport", back_populates="device")
    failure_records = relationship("FailureRecord", back_populates="device")
    creator = relationship("User", back_populates="created_devices")
