from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from src.auth.dependencies import get_current_admin_user, get_current_user
from src.part_types.dao import PartTypeDAO
from src.part_types.schemas import (
    SPartTypeRead,
    SPartTypeCreate,
    SPartTypeUpdate,
)

router = APIRouter(
    prefix="/part-types",
    tags=["Типы деталей"],
)


@router.get(
    "/", response_model=List[SPartTypeRead], summary="Список всех типов деталей"
)
async def list_part_types(
    current_user=Depends(get_current_user),
) -> List[SPartTypeRead]:
    try:
        pts = await PartTypeDAO.find_all()
        return [SPartTypeRead.model_validate(pt) for pt in pts]
    except SQLAlchemyError:
        raise HTTPException(500, "Database error while listing part types")


@router.get(
    "/{part_type_id}",
    response_model=SPartTypeRead,
    summary="Детали по конкретному типу детали",
)
async def get_part_type(
    part_type_id: int, current_user=Depends(get_current_user)
) -> SPartTypeRead:
    pt = await PartTypeDAO.find_by_id(part_type_id)
    if not pt:
        raise HTTPException(status_code=404, detail="PartType not found")
    return SPartTypeRead.model_validate(pt)


@router.post(
    "/",
    response_model=SPartTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый тип детали",
)
async def create_part_type(
    data: SPartTypeCreate, current_user=Depends(get_current_admin_user)
) -> SPartTypeRead:
    payload = data.model_dump()
    payload["created_by"] = current_user.id
    try:
        created = await PartTypeDAO.create(**payload)
        pt = await PartTypeDAO.find_by_id(created.id)
        return SPartTypeRead.model_validate(pt)
    except SQLAlchemyError:
        raise HTTPException(500, "Database error while creating part type")


@router.put(
    "/{part_type_id}", response_model=SPartTypeRead, summary="Обновить тип детали"
)
async def update_part_type(
    part_type_id: int,
    data: SPartTypeUpdate,
    current_user=Depends(get_current_admin_user),
) -> SPartTypeRead:
    existing = await PartTypeDAO.find_by_id(part_type_id)
    if not existing:
        raise HTTPException(status_code=404, detail="PartType not found")

    payload = data.model_dump(exclude_none=True)
    try:
        await PartTypeDAO.update(part_type_id, **payload)
        pt = await PartTypeDAO.find_by_id(part_type_id)
        return SPartTypeRead.model_validate(pt)
    except SQLAlchemyError:
        raise HTTPException(500, "Database error while updating part type")


@router.delete(
    "/{part_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тип детали",
)
async def delete_part_type(
    part_type_id: int, current_user=Depends(get_current_admin_user)
) -> Response:
    existing = await PartTypeDAO.find_by_id(part_type_id)
    if not existing:
        raise HTTPException(404, "PartType not found")
    try:
        await PartTypeDAO.delete(part_type_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError:
        raise HTTPException(500, "Database error while deleting part type")
