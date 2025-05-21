from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from src.auth.dependencies import get_current_user
from src.device_types.dao import DeviceTypeDAO
from src.device_types.schemas import (
    SDeviceTypeRead,
    SDeviceTypeCreate,
    SDeviceTypeUpdate,
)
from src.part_types.dao import PartTypeDAO

router = APIRouter(
    prefix="/device-types",
    tags=["Типы устройств"],
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "/",
    response_model=List[SDeviceTypeRead],
    summary="Список всех типов устройств"
)
async def list_device_types(
    offset: int = Query(0, ge=0),
    limit:  int = Query(100, ge=1, le=1000),
    part_type_id: Optional[int] = Query(None, description="Фильтр по типу детали")
) -> List[SDeviceTypeRead]:
    filters = {}
    if part_type_id is not None:
        filters["part_type_id"] = part_type_id

    dts = await DeviceTypeDAO.find_all(offset=offset, limit=limit, **filters)
    return [SDeviceTypeRead.model_validate(dt) for dt in dts]

@router.get(
    "/{type_id}",
    response_model=SDeviceTypeRead,
    summary="Детальная информация о типе устройства"
)
async def get_device_type(type_id: int) -> SDeviceTypeRead:
    dt = await DeviceTypeDAO.find_by_id(type_id)
    if not dt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DeviceType not found")
    return SDeviceTypeRead.model_validate(dt)

@router.post(
    "/",
    response_model=SDeviceTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового типа устройства"
)
async def create_device_type(data: SDeviceTypeCreate) -> SDeviceTypeRead:
    pt = await PartTypeDAO.find_by_id(data.part_type_id)
    if not pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PartType not found")

    created = await DeviceTypeDAO.create(**data.model_dump())
    dt = await DeviceTypeDAO.find_by_id(created.id)
    return SDeviceTypeRead.model_validate(dt)

@router.put(
    "/{type_id}",
    response_model=SDeviceTypeRead,
    summary="Обновление существующего типа устройства"
)
async def update_device_type(type_id: int, data: SDeviceTypeUpdate) -> SDeviceTypeRead:
    payload = data.model_dump(exclude_none=True)
    if "part_type_id" in payload:
        pt = await PartTypeDAO.find_by_id(payload["part_type_id"])
        if not pt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PartType not found")

    updated = await DeviceTypeDAO.update(type_id, **payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DeviceType not found")

    dt = await DeviceTypeDAO.find_by_id(type_id)
    return SDeviceTypeRead.model_validate(dt)

@router.delete(
    "/{type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление типа устройства"
)
async def delete_device_type(type_id: int) -> Response:
    success = await DeviceTypeDAO.delete(type_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DeviceType not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
