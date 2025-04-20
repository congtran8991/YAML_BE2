from typing import TYPE_CHECKING, List, Any, ByteString
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.group_datasets.schema import GroupDatasetCreateRequest, GroupDatasetResponse
from apps.group_datasets.service import (
    get_all_group_datasets,
    create_group_dataset,
    get_group_dataset_detail,
)
from database.postgresql import get_db

# if TYPE_CHECKING:
#     from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/api/group-datasets", response_model=List[GroupDatasetResponse])
async def get_all_group_datasets_db(
    request: Request, db: AsyncSession = Depends(get_db)
):
    user = request.state.user
    return await get_all_group_datasets(db=db, user=user)


@router.get(
    "/api/group-datasets/{group_dataset_id}", response_model=GroupDatasetResponse
)
async def get_group_datasets(
    request: Request, group_dataset_id: int, db: AsyncSession = Depends(get_db)
):
    user = request.state.user
    return await get_group_dataset_detail(
        group_dataset_id=group_dataset_id, db=db, user=user
    )


@router.post("/api/group-datasets", response_model=Any)
async def created_group_dataset(
    request: Request,
    requestBody: GroupDatasetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    return await create_group_dataset(db=db, user=user, requestBody=requestBody)
