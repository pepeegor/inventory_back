from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.dependencies import get_current_user
from src.movements.dao import MovementDAO
from src.movements.schemas import SMovementRead, SMovementCreate
from src.devices.dao import DeviceDAO

router = APIRouter(
    prefix="/devices/{device_id}/movements",
    tags=["Перемещения устройств"],
)

@router.get(
    "/",
    response_model=List[SMovementRead],
    summary="История перемещений устройства",
    dependencies=[Depends(get_current_user)]
)
async def list_movements(device_id: int) -> List[SMovementRead]:
    movements = await MovementDAO.find_by_device_id(device_id)
    return [SMovementRead.model_validate(m) for m in movements]

@router.post(
    "/",
    response_model=SMovementRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового перемещения",
    dependencies=[Depends(get_current_user)]
)
async def create_movement(
    device_id: int,
    data: SMovementCreate,
    current_user=Depends(get_current_user)
) -> SMovementRead:
    device = await DeviceDAO.find_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Устройство не найдено"
        )
    if data.from_location_id is not None and device.current_location_id != data.from_location_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device current_location_id does not match provided from_location_id"
        )
    data_dict = data.model_dump(exclude_none=True)
    data_dict['performed_by'] = current_user.id
    created = await MovementDAO.create(device_id=device_id, **data_dict)
    await DeviceDAO.update(device_id, current_location_id=created.to_location_id)
    movement = await MovementDAO.find_by_id(created.id)
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )
    return SMovementRead.model_validate(movement)