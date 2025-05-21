from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, Boolean, String, Text
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.inventory_events.models import InventoryEvent
    from src.devices.models import Device

class InventoryItem(Base):
    __tablename__ = 'inventory_items'

    id = Column(BigInteger, primary_key=True)
    inventory_event_id = Column(BigInteger, ForeignKey('inventory_events.id'), nullable=False)
    device_id = Column(BigInteger, ForeignKey('devices.id'), nullable=False)
    found = Column(Boolean, nullable=False)
    condition = Column(String(50))
    comments = Column(Text)

    event = relationship('InventoryEvent', back_populates='items')  # type: "InventoryEvent"
    device = relationship('Device', back_populates='inventory_items')  # type: "Device"