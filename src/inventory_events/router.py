from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.auth.dependencies import get_current_user
from src.inventory_events.dao import InventoryEventDAO
from src.inventory_events.schemas import (
    SInventoryEventRead,
    SInventoryEventCreate,
    SInventoryEventUpdate,
)

router = APIRouter(
    prefix="/inventory-events",
    tags=["События инвентаризации"],
)


@router.get(
    "/",
    response_model=List[SInventoryEventRead],
    summary="Список всех инвентаризаций",
    dependencies=[Depends(get_current_user)],
)
async def list_inventory_events(
    date_from: Optional[date] = Query(None, description="Начало диапазона дат"),
    date_to: Optional[date] = Query(None, description="Конец диапазона дат"),
    location_id: Optional[int] = Query(None, description="Фильтр по локации"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
) -> List[SInventoryEventRead]:
    events = await InventoryEventDAO.find_all(
        date_from=date_from,
        date_to=date_to,
        location_id=location_id,
        user_id=current_user.id,
        is_admin=current_user.role == "admin",
        offset=offset,
        limit=limit,
    )
    return [SInventoryEventRead.model_validate(e) for e in events]


@router.get(
    "/{event_id}",
    response_model=SInventoryEventRead,
    summary="Детали события и список позиций",
    dependencies=[Depends(get_current_user)],
)
async def get_inventory_event(event_id: int) -> SInventoryEventRead:
    event = await InventoryEventDAO.find_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return SInventoryEventRead.model_validate(event)


@router.post(
    "/",
    response_model=SInventoryEventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать событие инвентаризации",
)
async def create_event(
    data: SInventoryEventCreate, current_user=Depends(get_current_user)
) -> SInventoryEventRead:
    payload = data.model_dump(exclude_none=True)
    payload["performed_by"] = current_user.id
    created = await InventoryEventDAO.create(**payload)
    event = await InventoryEventDAO.find_by_id(created.id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return SInventoryEventRead.model_validate(event)


@router.put(
    "/{event_id}",
    response_model=SInventoryEventRead,
    summary="Обновить событие инвентаризации",
    dependencies=[Depends(get_current_user)],
)
async def update_inventory_event(
    event_id: int, data: SInventoryEventUpdate
) -> SInventoryEventRead:
    updated = await InventoryEventDAO.update(
        event_id, **data.model_dump(exclude_none=True)
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    event = await InventoryEventDAO.find_by_id(event_id)
    return SInventoryEventRead.model_validate(event)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить событие инвентаризации",
    dependencies=[Depends(get_current_user)],
)
async def delete_inventory_event(event_id: int):
    success = await InventoryEventDAO.delete(event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return None
