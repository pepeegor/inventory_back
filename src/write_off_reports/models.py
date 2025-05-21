from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.devices.models import Device
    from src.users.models import User

class WriteOffReport(Base):
    __tablename__ = 'write_off_reports'

    id = Column(BigInteger, primary_key=True)
    device_id = Column(BigInteger, ForeignKey('devices.id'), nullable=False)
    report_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    disposed_by = Column(BigInteger, ForeignKey('users.id'))
    approved_by = Column(BigInteger, ForeignKey('users.id'))

    device = relationship('Device', back_populates='write_off_reports')  # type: "Device"
    disposed_by_user = relationship(
        'User', back_populates='write_offs_disposed', foreign_keys=[disposed_by]
    )  # type: "User"
    approved_by_user = relationship(
        'User', back_populates='write_offs_approved', foreign_keys=[approved_by]
    )  # type: "User"