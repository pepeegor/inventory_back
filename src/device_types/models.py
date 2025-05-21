from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, String, Integer
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.devices.models import Device
    from src.part_types.models import PartType

class DeviceType(Base):
    __tablename__ = 'device_types'

    id = Column(BigInteger, primary_key=True)
    manufacturer = Column(String(100))
    model = Column(String(100))
    expected_lifetime_months = Column(Integer)
    part_type_id = Column(BigInteger, ForeignKey('part_types.id'), nullable=False)

    devices = relationship('Device', back_populates='type')
    part_types = relationship(
        "PartType",
        back_populates="device_types"
    )