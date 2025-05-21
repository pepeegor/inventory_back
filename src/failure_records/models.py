from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.devices.models import Device
    from src.part_types.models import PartType

class FailureRecord(Base):
    __tablename__ = 'failure_records'

    id = Column(BigInteger, primary_key=True)
    device_id = Column(BigInteger, ForeignKey('devices.id'), nullable=False)
    part_type_id = Column(BigInteger, ForeignKey('part_types.id'), nullable=False)
    failure_date = Column(Date, nullable=False)
    resolved_date = Column(Date)
    description = Column(Text)

    device = relationship('Device', back_populates='failure_records')  
    part_type = relationship('PartType', back_populates='failure_records')  