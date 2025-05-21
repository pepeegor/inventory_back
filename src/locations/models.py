from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.devices.models import Device
    from src.movements.models import Movement
    from src.inventory_events.models import InventoryEvent

class Location(Base):
    __tablename__ = 'locations'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(BigInteger, ForeignKey('locations.id'), nullable=True)
    description = Column(Text)

    parent = relationship('Location', remote_side=[id], back_populates='children')  # type: "Location"
    children = relationship('Location', back_populates='parent')  # type: list["Location"]

    devices = relationship('Device', back_populates='current_location')  # type: list["Device"]
    movements_from = relationship(
        'Movement', back_populates='from_location', foreign_keys='Movement.from_location_id'
    )  # type: list["Movement"]
    movements_to = relationship(
        'Movement', back_populates='to_location', foreign_keys='Movement.to_location_id'
    )  # type: list["Movement"]
    inventory_events = relationship('InventoryEvent', back_populates='location')  # type: list["InventoryEvent"]