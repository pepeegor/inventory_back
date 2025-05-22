from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from src.auth.dependencies import get_current_user
from src.failure_records.dao import FailureRecordDAO
from src.failure_records.schemas import (
    SFailureRecordRead,
    SFailureRecordCreate,
    SFailureRecordUpdate
)
from src.devices.dao import DeviceDAO

router = APIRouter(
    tags=["Записи об отказах"],
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "/devices/{device_id}/failures",
    response_model=List[SFailureRecordRead],
    summary="История отказов по устройству"
)
async def list_failures_by_device(
    device_id: int,
    current_user=Depends(get_current_user),
) -> List[SFailureRecordRead]:
    device = await DeviceDAO.find_by_id(device_id, creator_id=current_user.id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    try:
        recs = await FailureRecordDAO.find_by_device_id(
            device_id, creator_id=current_user.id
        )
        return [SFailureRecordRead.model_validate(r) for r in recs]
    except ValidationError:
        raise HTTPException(500, "Error serializing failure records")
    except SQLAlchemyError:
        raise HTTPException(500, "Database error while listing failures")

@router.get(
    "/part-types/{part_type_id}/failures",
    response_model=List[SFailureRecordRead],
    summary="Все отказы по типу детали"
)
async def list_failures_by_part_type(
    part_type_id: int,
    current_user=Depends(get_current_user),
) -> List[SFailureRecordRead]:
    try:
        recs = await FailureRecordDAO.find_by_part_type_id(
            part_type_id, creator_id=current_user.id
        )
        return [SFailureRecordRead.model_validate(r) for r in recs]
    except ValidationError:
        raise HTTPException(500, "Error serializing failure records")
    except SQLAlchemyError:
        raise HTTPException(500, "Database error while listing failures")

@router.post(
    "/failure-records",
    response_model=SFailureRecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать запись об отказе"
)
async def create_failure_record(
    data: SFailureRecordCreate,
    current_user=Depends(get_current_user),
) -> SFailureRecordRead:
    device = await DeviceDAO.find_by_id(data.device_id, creator_id=current_user.id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    part_type_id = device.type.part_type_id

    created = await FailureRecordDAO.create(
        device_id=data.device_id,
        part_type_id=part_type_id,
        failure_date=data.failure_date,
        description=data.description,
    )
    try:
        await DeviceDAO.update(data.device_id, status="failed")
    except SQLAlchemyError:
        pass

    record = await FailureRecordDAO.find_by_id(
        created.id, creator_id=current_user.id
    )
    return SFailureRecordRead.model_validate(record)

@router.put(
    "/failure-records/{failure_id}",
    response_model=SFailureRecordRead,
    summary="Обновить запись об отказе"
)
async def update_failure_record(
    failure_id: int,
    data: SFailureRecordUpdate,
    current_user=Depends(get_current_user),
) -> SFailureRecordRead:
    existing = await FailureRecordDAO.find_by_id(failure_id, creator_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="FailureRecord not found")

    updated = await FailureRecordDAO.update(failure_id, **data.model_dump(exclude_none=True))
    record = await FailureRecordDAO.find_by_id(failure_id, creator_id=current_user.id)
    return SFailureRecordRead.model_validate(record)

@router.delete(
    "/failure-records/{failure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить запись об отказе"
)
async def delete_failure_record(
    failure_id: int,
    current_user=Depends(get_current_user),
) -> Response:
    existing = await FailureRecordDAO.find_by_id(failure_id, creator_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="FailureRecord not found")

    await FailureRecordDAO.delete(failure_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
