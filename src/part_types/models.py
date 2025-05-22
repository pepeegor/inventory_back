from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, Integer
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.failure_records.models import FailureRecord
    from src.replacement_suggestions.models import ReplacementSuggestion
    from src.device_types.models import DeviceType

class PartType(Base):
    __tablename__ = 'part_types'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    expected_failure_interval_days = Column(Integer)

    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    failure_records = relationship('FailureRecord', back_populates='part_type') 
    replacement_suggestions = relationship('ReplacementSuggestion', back_populates='part_type') 
    device_types = relationship(
        "DeviceType",
        back_populates="part_types"
    )
    creator = relationship('User', back_populates='created_part_types')