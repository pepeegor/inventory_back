from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.movements.models import Movement
    from src.inventory_events.models import InventoryEvent
    from src.maintenance_tasks.models import MaintenanceTask
    from src.write_off_reports.models import WriteOffReport
    from src.devices.models import Device


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)

    movements = relationship(
        "Movement", back_populates="performed_by_user"
    ) 
    inventory_events = relationship(
        "InventoryEvent", back_populates="performed_by_user"
    )  
    maintenance_tasks = relationship(
        "MaintenanceTask", back_populates="assigned_user"
    ) 
    write_offs_disposed = relationship(
        "WriteOffReport",
        back_populates="disposed_by_user",
        foreign_keys="WriteOffReport.disposed_by",
    )  
    write_offs_approved = relationship(
        "WriteOffReport",
        back_populates="approved_by_user",
        foreign_keys="WriteOffReport.approved_by",
    )  
    created_device_types = relationship(
        "DeviceType", back_populates="creator", foreign_keys="DeviceType.created_by"
    )
    locations_created = relationship("Location", back_populates="creator")
    created_part_types = relationship(
        "PartType",
        back_populates="creator",
        foreign_keys="PartType.created_by",
    )
    created_devices = relationship(
        "Device", back_populates="creator"
    )  
