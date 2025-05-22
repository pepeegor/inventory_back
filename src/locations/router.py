from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.auth.dependencies import get_current_admin_user, get_current_user
from src.locations.dao import LocationDAO
from src.locations.schemas import (
    SLocationRead,
    SLocationCreate,
    SLocationUpdate,
)
from src.locations.utils import build_tree

router = APIRouter(
    prefix="/locations",
    tags=["Локации"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=List[SLocationRead], summary="Дерево локаций")
async def list_locations() -> List[SLocationRead]:
    all_locs = await LocationDAO.find_all()
    return build_tree(all_locs)

@router.get("/{location_id}", response_model=SLocationRead, summary="Информация по локации")
async def get_location(location_id: int) -> SLocationRead:
    loc = await LocationDAO.find_by_id(location_id)
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return SLocationRead.model_validate(loc)

@router.post(
    "/",
    response_model=SLocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой локации",
    dependencies=[Depends(get_current_admin_user)] 
)
async def create_location(
    data: SLocationCreate,
    current_user = Depends(get_current_admin_user)
) -> SLocationRead:
    payload = data.model_dump()
    payload["created_by"] = current_user.id
    created = await LocationDAO.create(**payload)
    loc = await LocationDAO.find_by_id(created.id)
    return SLocationRead.model_validate(loc)


@router.put("/{location_id}", response_model=SLocationRead, summary="Обновление локации")
async def update_location(location_id: int, data: SLocationUpdate) -> SLocationRead:
    updated = await LocationDAO.update(location_id, **data.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    # заново получить с отношениями
    loc = await LocationDAO.find_by_id(location_id)
    return SLocationRead.model_validate(loc)

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление локации")
async def delete_location(location_id: int) -> Response:
    success = await LocationDAO.delete(location_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)