from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, ForeignKey, Date, String, Text
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from src.part_types.models import PartType

class ReplacementSuggestion(Base):
    __tablename__ = 'replacement_suggestions'

    id = Column(BigInteger, primary_key=True)
    part_type_id = Column(BigInteger, ForeignKey('part_types.id'), nullable=False)
    suggestion_date = Column(Date, nullable=False)
    forecast_replacement_date = Column(Date, nullable=False)
    generated_by = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    comments = Column(Text)

    part_type = relationship('PartType', back_populates='replacement_suggestions')  