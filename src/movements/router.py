from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.auth.dependencies import get_current_user, get_current_admin_user
from src.movements.dao import MovementDAO
from src.movements.schemas import SMovementRead, SMovementCreate
from src.devices.dao import DeviceDAO

router = APIRouter(
    prefix="/devices/{device_id}/movements",
    tags=["Перемещения устройств"],
)

# Создаем отдельный роутер для админского эндпоинта
admin_router = APIRouter(
    prefix="/movements",
    tags=["Перемещения устройств (админ)"],
)


@admin_router.get(
    "/",
    response_model=List[SMovementRead],
    summary="Список всех перемещений (только для админов)",
)
async def list_all_movements(
    device_id: Optional[int] = Query(None, description="Фильтр по устройству"),
    performed_by: Optional[int] = Query(None, description="Фильтр по исполнителю"),
    from_location_id: Optional[int] = Query(
        None, description="Фильтр по начальной локации"
    ),
    to_location_id: Optional[int] = Query(
        None, description="Фильтр по конечной локации"
    ),
    moved_from: Optional[datetime] = Query(
        None, description="Фильтр по дате перемещения (от)"
    ),
    moved_to: Optional[datetime] = Query(
        None, description="Фильтр по дате перемещения (до)"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_admin_user),
) -> List[SMovementRead]:
    movements = await MovementDAO.find_all(
        device_id=device_id,
        performed_by=performed_by,
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        moved_from=moved_from,
        moved_to=moved_to,
        offset=offset,
        limit=limit,
    )
    return [SMovementRead.model_validate(m) for m in movements]


@router.get(
    "/",
    response_model=List[SMovementRead],
    summary="История перемещений устройства",
    dependencies=[Depends(get_current_user)],
)
async def list_movements(
    device_id: int, current_user=Depends(get_current_user)
) -> List[SMovementRead]:
    movements = await MovementDAO.find_by_device_id(device_id, user_id=current_user.id)
    return [SMovementRead.model_validate(m) for m in movements]


@router.post(
    "/",
    response_model=SMovementRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового перемещения",
    dependencies=[Depends(get_current_user)],
)
async def create_movement(
    device_id: int, data: SMovementCreate, current_user=Depends(get_current_user)
) -> SMovementRead:
    device = await DeviceDAO.find_by_id(device_id, creator_id=current_user.id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Устройство не найдено"
        )
    if (
        data.from_location_id is not None
        and device.current_location_id != data.from_location_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device current_location_id does not match provided from_location_id",
        )
    data_dict = data.model_dump(exclude_none=True)
    data_dict["performed_by"] = current_user.id
    created = await MovementDAO.create(device_id=device_id, **data_dict)
    await DeviceDAO.update(device_id, current_location_id=created.to_location_id)
    movement = await MovementDAO.find_by_id(created.id)
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movement not found"
        )
    return SMovementRead.model_validate(movement)
