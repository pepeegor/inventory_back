from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from src.devices.dao import DeviceDAO
from src.auth.dependencies import get_current_user
from src.maintenance_tasks.dao import MaintenanceTaskDAO
from src.maintenance_tasks.schemas import (
    SMaintenanceTaskRead,
    SMaintenanceTaskCreate,
    SMaintenanceTaskUpdate,
)

router = APIRouter(
    prefix="/maintenance-tasks",
    tags=["Регламентные работы"],
)


@router.get(
    "/",
    response_model=List[SMaintenanceTaskRead],
    summary="Список всех задач регламентных работ",
)
async def list_tasks(
    device_id: Optional[int] = Query(None, description="Фильтр по устройству"),
    assigned_to: Optional[int] = Query(None, description="Фильтр по исполнителю"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    scheduled_from: Optional[date] = Query(None, description="Дата начала"),
    scheduled_to: Optional[date] = Query(None, description="Дата конца"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
) -> List[SMaintenanceTaskRead]:
    tasks = await MaintenanceTaskDAO.find_all(
        device_id=device_id,
        assigned_to=assigned_to,
        status=status,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        creator_user_id=current_user.id,
        offset=offset,
        limit=limit,
    )
    return [SMaintenanceTaskRead.model_validate(t) for t in tasks]


@router.get(
    "/{task_id}",
    response_model=SMaintenanceTaskRead,
    summary="Детали задачи регламентной работы",
)
async def get_task(
    task_id: int,
    current_user=Depends(get_current_user),
) -> SMaintenanceTaskRead:
    task = await MaintenanceTaskDAO.find_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return SMaintenanceTaskRead.model_validate(task)


@router.post(
    "/",
    response_model=SMaintenanceTaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую задачу регламентной работы",
)
async def create_task(
    data: SMaintenanceTaskCreate,
    current_user=Depends(get_current_user),
) -> SMaintenanceTaskRead:
    device = await DeviceDAO.find_by_id(data.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id={data.device_id} not found",
        )

    payload = data.model_dump(exclude_none=True)
    payload["assigned_to"] = current_user.id

    created = await MaintenanceTaskDAO.create(**payload)

    task = await MaintenanceTaskDAO.find_by_id(created.id)
    return SMaintenanceTaskRead.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=SMaintenanceTaskRead,
    summary="Обновить задачу регламентной работы",
)
async def update_task(
    task_id: int,
    data: SMaintenanceTaskUpdate,
    current_user=Depends(get_current_user),
) -> SMaintenanceTaskRead:
    payload = data.model_dump(exclude_none=True)
    updated = await MaintenanceTaskDAO.update(task_id, **payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    task = await MaintenanceTaskDAO.find_by_id(task_id)
    return SMaintenanceTaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить задачу регламентной работы",
)
async def delete_task(
    task_id: int,
    current_user=Depends(get_current_user),
):
    success = await MaintenanceTaskDAO.delete(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
