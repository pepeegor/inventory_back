from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, String, Date, Text
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.devices.models import Device
    from src.users.models import User

class MaintenanceTask(Base):
    __tablename__ = 'maintenance_tasks'

    id = Column(BigInteger, primary_key=True)
    device_id = Column(BigInteger, ForeignKey('devices.id'), nullable=False)
    task_type = Column(String(100), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date)
    status = Column(String(20), nullable=False)
    assigned_to = Column(BigInteger, ForeignKey('users.id'))
    notes = Column(Text)

    device = relationship('Device', back_populates='maintenance_tasks')  # type: "Device"
    assigned_user = relationship('User', back_populates='maintenance_tasks')  # type: "User"