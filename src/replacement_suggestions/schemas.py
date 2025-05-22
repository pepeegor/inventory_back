from datetime import date
from typing import Optional
from src.schemas.base import OrmModel

class SPartTypeInSuggestion(OrmModel):
    id: int
    name: str

class SReplacementSuggestionBase(OrmModel):
    part_type_id: int
    forecast_replacement_date: date
    comments: Optional[str] = None

class SReplacementSuggestionCreate(SReplacementSuggestionBase):
    pass

class SReplacementSuggestionUpdate(OrmModel):
    status: Optional[str]  = None
    comments: Optional[str] = None

class SReplacementSuggestionRead(SReplacementSuggestionBase):
    id: int
    suggestion_date: date
    generated_by: str
    status:       str
    part_type:    SPartTypeInSuggestion
