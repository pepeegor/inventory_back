from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import SQLAlchemyError

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
)


@router.get(
    "/", response_model=List[SDeviceTypeRead], summary="Список своих типов устройств"
)
async def list_my_device_types(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    part_type_id: Optional[int] = Query(None, description="Фильтр по типу детали"),
    current_user=Depends(get_current_user),
):
    filters = {}
    if part_type_id is not None:
        filters["part_type_id"] = part_type_id

    try:
        items = await DeviceTypeDAO.find_all(
            offset=offset, limit=limit, creator_id=current_user.id, **filters
        )
        return [SDeviceTypeRead.model_validate(it) for it in items]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")


@router.get(
    "/{type_id}",
    response_model=SDeviceTypeRead,
    summary="Детальная информация о своём типе устройства",
)
async def get_my_device_type(type_id: int, current_user=Depends(get_current_user)):
    dt = await DeviceTypeDAO.find_by_id(type_id)
    if not dt or dt.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return SDeviceTypeRead.model_validate(dt)


@router.post(
    "/",
    response_model=SDeviceTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового типа устройства",
)
async def create_device_type(
    data: SDeviceTypeCreate, current_user=Depends(get_current_user)
):
    if not await PartTypeDAO.find_by_id(data.part_type_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PartType not found"
        )

    created = await DeviceTypeDAO.create(
        created_by=current_user.id, **data.model_dump()
    )
    return SDeviceTypeRead.model_validate(created)


@router.put(
    "/{type_id}",
    response_model=SDeviceTypeRead,
    summary="Обновление своего типа устройства",
)
async def update_device_type(
    type_id: int, data: SDeviceTypeUpdate, current_user=Depends(get_current_user)
):
    existing = await DeviceTypeDAO.find_by_id(type_id)
    if not existing or existing.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    payload = data.model_dump(exclude_none=True)
    if "part_type_id" in payload:
        if not await PartTypeDAO.find_by_id(payload["part_type_id"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="PartType not found"
            )

    updated = await DeviceTypeDAO.update(type_id, **payload)
    return SDeviceTypeRead.model_validate(updated)


@router.delete(
    "/{type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление своего типа устройства",
)
async def delete_device_type(type_id: int, current_user=Depends(get_current_user)):
    existing = await DeviceTypeDAO.find_by_id(type_id)
    if not existing or existing.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    await DeviceTypeDAO.delete(type_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
