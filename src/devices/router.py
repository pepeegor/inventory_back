from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

from src.auth.dependencies import get_current_user
from src.devices.dao import DeviceDAO
from src.devices.schemas import SDeviceRead, SDeviceCreate, SDeviceUpdate
from src.device_types.dao import DeviceTypeDAO
from src.locations.dao import LocationDAO

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/devices",
    tags=["Устройства"],
)


@router.get(
    "/",
    response_model=List[SDeviceRead],
    summary="Список устройств",
)
async def list_devices(
    type_id: Optional[int] = Query(None, description="Фильтр по типу устройства"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    current_location_id: Optional[int] = Query(
        None, description="Фильтр по текущей локации"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
) -> List[SDeviceRead]:
    devices = await DeviceDAO.find_all(
        creator_id=current_user.id,
        is_admin=current_user.role == "admin",
        type_id=type_id,
        status=status,
        current_location_id=current_location_id,
        offset=offset,
        limit=limit,
    )
    return [SDeviceRead.model_validate(d) for d in devices]


@router.get(
    "/{device_id}",
    response_model=SDeviceRead,
    summary="Детали устройства",
)
async def get_device(
    device_id: int, current_user=Depends(get_current_user)
) -> SDeviceRead:
    device = await DeviceDAO.find_by_id(
        device_id, creator_id=current_user.id, is_admin=current_user.role == "admin"
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id={device_id} not found",
        )
    return SDeviceRead.model_validate(device)


@router.post(
    "/",
    response_model=SDeviceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление нового устройства",
)
async def create_device(
    data: SDeviceCreate,
    current_user=Depends(get_current_user),
):
    try:
        if not await DeviceTypeDAO.find_by_id(data.type_id):
            raise HTTPException(404, "DeviceType not found")
        if data.current_location_id is not None:
            loc = await LocationDAO.find_by_id(
                data.current_location_id, creator_id=current_user.id
            )
            if not loc:
                raise HTTPException(404, "Location not found or not yours")

        # Добавляем created_by при создании устройства
        device_data = data.model_dump()
        device_data["created_by"] = current_user.id

        created = await DeviceDAO.create(**device_data)
        device = await DeviceDAO.find_by_id(created.id, creator_id=current_user.id)
        return SDeviceRead.model_validate(device)
    except IntegrityError:
        raise HTTPException(400, "Device with this serial_number already exists")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating device: {str(e)}")
        raise HTTPException(500, f"Database error while creating device: {str(e)}")
    except ValidationError as e:
        logger.error(f"Error serializing new device: {str(e)}")
        raise HTTPException(500, f"Error formatting device data: {str(e)}")


@router.put(
    "/{device_id}", response_model=SDeviceRead, summary="Редактирование устройства"
)
async def update_device(
    device_id: int,
    data: SDeviceUpdate,
    current_user=Depends(get_current_user),
):
    try:
        payload = data.model_dump(exclude_none=True)
        if payload.get("type_id") is not None:
            if not await DeviceTypeDAO.find_by_id(payload["type_id"]):
                raise HTTPException(404, "DeviceType not found")
        if payload.get("current_location_id") is not None:
            loc = await LocationDAO.find_by_id(payload["current_location_id"])
            if not loc:
                raise HTTPException(404, "Location not found or not yours")

        updated = await DeviceDAO.update(device_id, **payload)
        if not updated:
            raise HTTPException(404, "Device not found")

        device = await DeviceDAO.find_by_id(device_id, creator_id=current_user.id)
        return SDeviceRead.model_validate(device)
    except IntegrityError:
        raise HTTPException(400, "serial_number conflict")
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating device: {str(e)}")
        raise HTTPException(500, f"Database error while updating device: {str(e)}")
    except ValidationError as e:
        logger.error(f"Error serializing updated device: {str(e)}")
        raise HTTPException(500, f"Error formatting device data: {str(e)}")


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление устройства",
)
async def delete_device(
    device_id: int,
    current_user=Depends(get_current_user),
):
    try:
        device = await DeviceDAO.find_by_id(device_id, creator_id=current_user.id)
        if not device:
            raise HTTPException(404, "Device not found")
        await DeviceDAO.delete(device_id)
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting device: {str(e)}")
        raise HTTPException(500, f"Database error while deleting device: {str(e)}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
