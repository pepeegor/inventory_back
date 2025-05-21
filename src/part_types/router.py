from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.auth.dependencies import get_current_user
from src.part_types.dao import PartTypeDAO
from src.part_types.schemas import (
    SPartTypeRead,
    SPartTypeCreate,
    SPartTypeUpdate,
)
from src.device_types.dao import DeviceTypeDAO

router = APIRouter(
    prefix="/part-types",
    tags=["Типы деталей"],
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "/",
    response_model=List[SPartTypeRead],
    summary="Список всех типов деталей"
)
async def list_part_types() -> List[SPartTypeRead]:
    pts = await PartTypeDAO.find_all()
    return [SPartTypeRead.model_validate(pt) for pt in pts]

@router.get(
    "/{part_type_id}",
    response_model=SPartTypeRead,
    summary="Детали по конкретному типу детали"
)
async def get_part_type(part_type_id: int) -> SPartTypeRead:
    pt = await PartTypeDAO.find_by_id(part_type_id)
    if not pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PartType not found")
    return SPartTypeRead.model_validate(pt)

@router.post(
    "/",
    response_model=SPartTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый тип детали"
)
async def create_part_type(data: SPartTypeCreate) -> SPartTypeRead:
    created = await PartTypeDAO.create(**data.model_dump())
    pt = await PartTypeDAO.find_by_id(created.id)
    return SPartTypeRead.model_validate(pt)

@router.put(
    "/{part_type_id}",
    response_model=SPartTypeRead,
    summary="Обновить тип детали"
)
async def update_part_type(part_type_id: int, data: SPartTypeUpdate) -> SPartTypeRead:
    updated = await PartTypeDAO.update(part_type_id, **data.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PartType not found")
    pt = await PartTypeDAO.find_by_id(part_type_id)
    return SPartTypeRead.model_validate(pt)

@router.delete(
    "/{part_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тип детали"
)
async def delete_part_type(part_type_id: int) -> Response:
    success = await PartTypeDAO.delete(part_type_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PartType not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
