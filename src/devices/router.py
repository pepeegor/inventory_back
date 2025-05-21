from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.auth.dependencies import get_current_user
from src.devices.dao import DeviceDAO
from src.devices.schemas import SDeviceRead, SDeviceCreate, SDeviceUpdate
from src.device_types.dao import DeviceTypeDAO
from src.locations.dao import LocationDAO

router = APIRouter(
    prefix="/devices",
    tags=["Устройства"],
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "/",
    response_model=List[SDeviceRead],
    summary="Список всех устройств"
)
async def list_devices(
    type_id: Optional[int] = Query(None, description="Фильтр по типу"),
    status:  Optional[str] = Query(None, description="Фильтр по статусу"),
    current_location_id: Optional[int] = Query(None, description="Фильтр по локации"),
    offset: int = Query(0, ge=0),
    limit:  int = Query(100, ge=1, le=1000),
) -> List[SDeviceRead]:
    try:
        devices = await DeviceDAO.find_all(
            offset=offset,
            limit=limit,
            type_id=type_id,
            status=status,
            current_location_id=current_location_id
        )
        return [SDeviceRead.model_validate(d) for d in devices]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while listing devices")

@router.get(
    "/{device_id}",
    response_model=SDeviceRead,
    summary="Карточка устройства"
)
async def get_device(device_id: int) -> SDeviceRead:
    try:
        device = await DeviceDAO.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return SDeviceRead.model_validate(device)
    except ValidationError:
        raise HTTPException(status_code=500, detail="Error serializing device")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while fetching device")

@router.post(
    "/",
    response_model=SDeviceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление нового устройства"
)
async def create_device(data: SDeviceCreate) -> SDeviceRead:
    if not await DeviceTypeDAO.find_by_id(data.type_id):
        raise HTTPException(status_code=404, detail="DeviceType not found")
    if data.current_location_id is not None and not await LocationDAO.find_by_id(data.current_location_id):
        raise HTTPException(status_code=404, detail="Location not found")

    try:
        created = await DeviceDAO.create(**data.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Device with this serial_number already exists")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while creating device")

    try:
        device = await DeviceDAO.find_by_id(created.id)
        return SDeviceRead.model_validate(device)
    except ValidationError:
        raise HTTPException(status_code=500, detail="Error serializing new device")

@router.put(
    "/{device_id}",
    response_model=SDeviceRead,
    summary="Редактирование устройства"
)
async def update_device(device_id: int, data: SDeviceUpdate) -> SDeviceRead:
    payload = data.model_dump(exclude_none=True)
    if payload.get("type_id") is not None:
        if not await DeviceTypeDAO.find_by_id(payload["type_id"]):
            raise HTTPException(status_code=404, detail="DeviceType not found")
    if payload.get("current_location_id") is not None:
        if not await LocationDAO.find_by_id(payload["current_location_id"]):
            raise HTTPException(status_code=404, detail="Location not found")

    try:
        updated = await DeviceDAO.update(device_id, **payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Device not found")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="serial_number conflict")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while updating device")

    try:
        device = await DeviceDAO.find_by_id(device_id)
        return SDeviceRead.model_validate(device)
    except ValidationError:
        raise HTTPException(status_code=500, detail="Error serializing updated device")

@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление устройства"
)
async def delete_device(device_id: int) -> Response:
    try:
        success = await DeviceDAO.delete(device_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while deleting device")
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
