from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.locations.models import Location
    from src.users.models import User
    from src.inventory_items.models import InventoryItem

class InventoryEvent(Base):
    __tablename__ = 'inventory_events'

    id = Column(BigInteger, primary_key=True)
    event_date = Column(Date, nullable=False)
    location_id = Column(BigInteger, ForeignKey('locations.id'), nullable=False)
    performed_by = Column(BigInteger, ForeignKey('users.id'))
    notes = Column(Text)

    location = relationship('Location', back_populates='inventory_events') 
    performed_by_user = relationship('User', back_populates='inventory_events')  
    items = relationship('InventoryItem', back_populates='event')  