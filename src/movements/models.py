from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.devices.models import Device
    from src.locations.models import Location
    from src.users.models import User

class Movement(Base):
    __tablename__ = 'movements'

    id = Column(BigInteger, primary_key=True)
    device_id = Column(BigInteger, ForeignKey('devices.id'), nullable=False)
    from_location_id = Column(BigInteger, ForeignKey('locations.id'))
    to_location_id = Column(BigInteger, ForeignKey('locations.id'), nullable=False)
    moved_at = Column(TIMESTAMP(timezone=True), nullable=False)
    performed_by = Column(BigInteger, ForeignKey('users.id'))
    notes = Column(Text)

    device = relationship('Device', back_populates='movements')  # type: "Device"
    from_location = relationship(
        'Location', back_populates='movements_from', foreign_keys=[from_location_id]
    )  # type: "Location"
    to_location = relationship(
        'Location', back_populates='movements_to', foreign_keys=[to_location_id]
    )  # type: "Location"
    performed_by_user = relationship('User', back_populates='movements')  # type: "User"