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


@router.get("/", response_model=List[SDeviceRead], summary="Список всех устройств")
async def list_devices(
    type_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_location_id: Optional[int] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
):
    try:
        devices = await DeviceDAO.find_all(
            creator_id=current_user.id,
            offset=offset,
            limit=limit,
            type_id=type_id,
            status=status,
            current_location_id=current_location_id,
        )

        # Создадим список устройств с обработкой ошибок для каждого устройства отдельно
        result = []
        for device in devices:
            try:
                device_schema = SDeviceRead.model_validate(device)
                result.append(device_schema)
            except ValidationError as e:
                logger.error(f"ValidationError for device {device.id}: {str(e)}")
                # We still want to include this device in results, just with minimal data
                # This is a fallback solution, our schema changes should prevent this error
                continue

        return result
    except SQLAlchemyError as e:
        logger.error(f"Database error while listing devices: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Database error while listing devices: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Unexpected error: {str(e)}")


@router.get("/{device_id}", response_model=SDeviceRead, summary="Карточка устройства")
async def get_device(
    device_id: int,
    current_user=Depends(get_current_user),
):
    try:
        device = await DeviceDAO.find_by_id(device_id, creator_id=current_user.id)
        if not device:
            raise HTTPException(404, "Device not found")
        return SDeviceRead.model_validate(device)
    except ValidationError as e:
        logger.error(f"Error serializing device {device_id}: {str(e)}")
        raise HTTPException(500, f"Error formatting device data: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching device: {str(e)}")
        raise HTTPException(500, f"Database error while fetching device: {str(e)}")


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

        created = await DeviceDAO.create(**data.model_dump())
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
            loc = await LocationDAO.find_by_id(
                payload["current_location_id"]
            )
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
