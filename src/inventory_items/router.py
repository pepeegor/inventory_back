from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.devices.dao import DeviceDAO
from src.auth.dependencies import get_current_user
from src.inventory_items.dao import InventoryItemDAO
from src.inventory_items.schemas import (
    SInventoryItemRead,
    SInventoryItemCreate,
    SInventoryItemUpdate
)
from src.inventory_events.dao import InventoryEventDAO

router = APIRouter(tags=["Инвентаризация по устройству"])

@router.post(
    "/inventory-events/{event_id}/items",
    response_model=SInventoryItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить результат инвентаризации по устройству",
    dependencies=[Depends(get_current_user)]
)
async def create_inventory_item(
    event_id: int,
    data: SInventoryItemCreate
) -> SInventoryItemRead:
    event = await InventoryEventDAO.find_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="InventoryEvent not found")

    device = await DeviceDAO.find_by_id(data.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.current_location_id != event.location_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Device (id={device.id}) находится в локации "
                f"{device.current_location_id}, а не в {event.location_id}"
            )
        )

    existing = await InventoryItemDAO.find_one_or_none(
        inventory_event_id=event_id,
        device_id=data.device_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Результат инвентаризации для device_id={data.device_id} уже существует"
        )

    payload = data.model_dump(exclude_none=True)
    payload["inventory_event_id"] = event_id
    created = await InventoryItemDAO.create(**payload)
    return SInventoryItemRead.model_validate(created)


@router.put(
    "/inventory-items/{item_id}",
    response_model=SInventoryItemRead,
    summary="Обновить запись результата инвентаризации",
    dependencies=[Depends(get_current_user)]
)
async def update_inventory_item(
    item_id: int,
    data: SInventoryItemUpdate
) -> SInventoryItemRead:
    payload = data.model_dump(exclude_none=True)
    updated = await InventoryItemDAO.update(item_id, **payload)
    if not updated:
        raise HTTPException(status_code=404, detail="InventoryItem not found")
    return SInventoryItemRead.model_validate(updated)


@router.delete(
    "/inventory-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить запись результата инвентаризации",
    dependencies=[Depends(get_current_user)]
)
async def delete_inventory_item(item_id: int):
    deleted = await InventoryItemDAO.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="InventoryItem not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
