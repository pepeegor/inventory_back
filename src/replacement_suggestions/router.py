# src/replacement_suggestions/router.py

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.auth.dependencies import get_current_user
from src.replacement_suggestions.dao import ReplacementSuggestionDAO
from src.replacement_suggestions.schemas import (
    SReplacementSuggestionRead,
    SReplacementSuggestionCreate,
    SReplacementSuggestionUpdate
)
from src.part_types.dao import PartTypeDAO

router = APIRouter(
    tags=["Предложения по замене устройств"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/replacement-suggestions",
    response_model=List[SReplacementSuggestionRead],
    summary="Все предложения (с фильтрацией)"
)
async def list_suggestions(
    part_type_id: Optional[int] = Query(None, description="Фильтр по типу детали"),
    status:        Optional[str] = Query(None, description="Фильтр по статусу"),
    date_from:     Optional[date] = Query(None, description="Дата от"),
    date_to:       Optional[date] = Query(None, description="Дата до"),
) -> List[SReplacementSuggestionRead]:
    try:
        items = await ReplacementSuggestionDAO.find_all(
            part_type_id=part_type_id,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
        return [SReplacementSuggestionRead.model_validate(i) for i in items]
    except ValidationError:
        raise HTTPException(status_code=500, detail="Error serializing suggestions")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while listing suggestions")


@router.get(
    "/part-types/{part_type_id}/replacement-suggestions",
    response_model=List[SReplacementSuggestionRead],
    summary="Предложения для выбранного типа детали"
)
async def list_by_part_type(part_type_id: int) -> List[SReplacementSuggestionRead]:
    if not await PartTypeDAO.find_by_id(part_type_id):
        raise HTTPException(status_code=404, detail="PartType not found")
    try:
        items = await ReplacementSuggestionDAO.find_all(part_type_id=part_type_id)
        return [SReplacementSuggestionRead.model_validate(i) for i in items]
    except ValidationError:
        raise HTTPException(status_code=500, detail="Error serializing suggestions")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while listing suggestions")


@router.put(
    "/replacement-suggestions/{suggestion_id}",
    response_model=SReplacementSuggestionRead,
    summary="Обновить статус или комментарий"
)
async def update_suggestion(
    suggestion_id: int,
    data: SReplacementSuggestionUpdate
) -> SReplacementSuggestionRead:
    payload = data.model_dump(exclude_none=True)
    try:
        updated = await ReplacementSuggestionDAO.update(suggestion_id, **payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Suggestion not found")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while updating suggestion")

    try:
        item = await ReplacementSuggestionDAO.find_by_id(suggestion_id)
        return SReplacementSuggestionRead.model_validate(item)
    except ValidationError:
        raise HTTPException(status_code=500, detail="Error serializing updated suggestion")


@router.delete(
    "/replacement-suggestions/{suggestion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить предложение"
)
async def delete_suggestion(suggestion_id: int) -> Response:
    try:
        success = await ReplacementSuggestionDAO.delete(suggestion_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while deleting suggestion")
    if not success:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
